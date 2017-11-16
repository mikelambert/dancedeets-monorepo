/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import querystring from 'querystring';
import { feed } from '../api/dancedeets';

const YoutubeKey = 'AIzaSyCV8QCRxSwv1vVk017qI3EZ9zlC8TefUjY';

export type BlogPost = {
  title: string,
  preview: string,
  postTime: number,
  author: string,
  url: string,
};

export class Blog {
  title: string;
  description: string;
  url: string;
  authorLookup: { [key: string]: string };
  posts: BlogPost[];
}

export class MediumBlog extends Blog {
  constructor(json: any) {
    super();
    const realPosts: Array<any> = Object.values(json.payload.references.Post);
    const users = json.payload.references.User;
    this.title = json.payload.value.name;
    this.description = json.payload.value.shortDescription;
    this.url = `https://medium.com/${json.payload.value.slug}`;
    this.authorLookup = Object.keys(users).reduce(
      (previous, x) => ({ ...previous, [x]: users[x].name }),
      {}
    );
    this.posts = realPosts.map(x => this.parseMediumPost(x));
  }

  parseMediumPost(realPost: any): BlogPost {
    const url = `${this.url}/${realPost.uniqueSlug}`;
    return {
      title: realPost.title,
      preview: realPost.virtuals.snippet,
      postTime: realPost.createdAt,
      author: this.authorLookup[realPost.creatorId],
      url,
    };
  }

  static async load(name: string) {
    const feedName = `https://medium.com/${name}?format=json`;
    const result = await fetch(feedName);
    const fullText = await result.text();
    const text = fullText.substring(fullText.indexOf('{'));
    const json = JSON.parse(text);
    return new MediumBlog(json);
  }
}

export class FeedBlog extends Blog {
  constructor(json: any) {
    super();
    const realPosts: [] = json.entries;
    this.title = json.feed.title;
    this.description = json.feed.subtitle;
    this.url = json.feed.link;
    this.posts = realPosts.map(x => this.parseFeedPost(x));
  }

  parseFeedPost(realPost: any): BlogPost {
    return {
      title: realPost.title,
      preview: realPost.summary,
      postTime: realPost.published_parsed,
      author: realPost.author,
      url: realPost.link,
    };
  }

  static async load(url: string) {
    const json = await feed(url);
    return new FeedBlog(json);
  }
}

export class YoutubePlaylistBlog extends Blog {
  constructor(playlistJson: any, playlistItemsJson: any, videosJson: any) {
    super();
    this.title = playlistJson.items[0].snippet.title;
    this.description = playlistJson.items[0].snippet.description;
    this.url = `https://www.youtube.com/playlist?list=${playlistJson.items[0]
      .id}`;

    const contentDetailsLookup = {};
    videosJson.items.forEach(x => {
      contentDetailsLookup[x.id] = x.contentDetails;
    });
    // Filter out any private/deleted videos which we can't access contentDetails for
    const filteredPlaylistItems = playlistItemsJson.items.filter(
      x => contentDetailsLookup[x.snippet.resourceId.videoId]
    );

    this.posts = filteredPlaylistItems.map(x =>
      this.parsePlaylistItem(
        x.snippet,
        contentDetailsLookup[x.snippet.resourceId.videoId]
      )
    );
  }

  author() {
    // TODO: Fix this!
    return this.posts[0].author;
  }

  parsePlaylistItem(snippet: any, contentDetails: any): BlogPost {
    return {
      title: snippet.title,
      preview: snippet.description,
      postTime: snippet.publishedAt,
      author: snippet.channelTitle,
      url: `https://www.youtube.com/watch?v=${snippet.resourceId.videoId}`,
      youtubeId: snippet.resourceId.videoId,
    };
  }

  static getUrl(path: string, args: Object) {
    const formattedArgs = querystring.stringify(args);
    let fullPath = path;
    if (formattedArgs) {
      fullPath += `?${formattedArgs}`;
    }
    return fullPath;
  }

  static async getTimes(playlistItemsJson: any) {
    const videoIds = playlistItemsJson.items.map(
      x => x.snippet.resourceId.videoId
    );
    const playlistItemsUrl = YoutubePlaylistBlog.getUrl(
      'https://www.googleapis.com/youtube/v3/videos',
      {
        id: videoIds.join(','),
        maxResults: 50,
        part: 'contentDetails',
        key: YoutubeKey,
      }
    );
    const videosResult = await (await fetch(playlistItemsUrl)).json();
    return videosResult;
  }

  static async load(playlistId: string) {
    const playlistItemsUrl = YoutubePlaylistBlog.getUrl(
      'https://www.googleapis.com/youtube/v3/playlistItems',
      {
        playlistId,
        maxResults: 50,
        part: 'snippet',
        key: YoutubeKey,
      }
    );
    const playlistUrl = YoutubePlaylistBlog.getUrl(
      'https://www.googleapis.com/youtube/v3/playlists',
      {
        id: playlistId,
        part: 'snippet',
        key: YoutubeKey,
      }
    );
    const playlistItemsResult = await (await fetch(playlistItemsUrl)).json();
    const videosResult = await YoutubePlaylistBlog.getTimes(
      playlistItemsResult
    );
    const playlistResult = await (await fetch(playlistUrl)).json();
    return new YoutubePlaylistBlog(
      playlistResult,
      playlistItemsResult,
      videosResult
    );
  }
}
