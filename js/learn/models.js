/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { feed } from '../api/dancedeets';

const YoutubeKey = 'AIzaSyCV8QCRxSwv1vVk017qI3EZ9zlC8TefUjY';

export type BlogPost = {
  title: string;
  preview: string;
  postTime: number;
  author: string;
  url: string;
};

export class Blog {
  title: string;
  description: string;
  url: string;
  authorLookup: { [key: string]: string };
  posts: [BlogPost];
}

export class MediumBlog extends Blog {
  constructor(json: any) {
    super();
    const realPosts: [any] = Object.values(json.payload.references.Post);
    const users = json.payload.references.User;
    this.title = json.payload.value.name;
    this.description = json.payload.value.shortDescription;
    this.url = `https://medium.com/${json.payload.value.slug}`;
    this.authorLookup = Object.keys(users).reduce(function(previous, x) {
      previous[x] = users[x].name;
      return previous;
    }, {});
    this.posts = realPosts.map((x) => this.parseMediumPost(x));
  }

  parseMediumPost(realPost: any): BlogPost {
    const url = `${this.url}/${realPost.uniqueSlug}`;
    return {
      title: realPost.title,
      preview: realPost.virtuals.snippet,
      postTime: realPost.createdAt,
      author: this.authorLookup[realPost.creatorId],
      url: url,
    };
  }

  static async load(name) {
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
    const realPosts: [any] = json.entries;
    this.title = json.feed.title;
    this.description = json.feed.subtitle;
    this.url = json.feed.link;
    this.posts = realPosts.map((x) => this.parseFeedPost(x));
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

  static async load(url) {
    const json = await feed(url);
    return new FeedBlog(json);
  }
}

export class YoutubePlaylistBlog extends Blog {
  constructor(playlistJson: any, playlistItemsJson: any) {
    super();
    this.title = playlistJson.items[0].snippet.title;
    this.description = playlistJson.items[0].snippet.description;
    this.url = `https://www.youtube.com/playlist?list=${playlistJson.items[0].id}`;
    this.posts = playlistItemsJson.items.map((x) => this.parsePlaylistItem(x));
  }

  parsePlaylistItem(item: any): BlogPost {
    return {
      title: item.snippet.title,
      preview: item.snippet.description,
      postTime: item.snippet.publishedAt,
      author: item.snippet.channelTitle,
      url: `https://www.youtube.com/watch?v=${item.snippet.resourceId.videoId}`,
      youtubeId: item.snippet.resourceId.videoId,
    };
  }

  static getUrl(path: string, args: Object) {
    const querystring = require('querystring');
    const formattedArgs = querystring.stringify(args);
    var fullPath = path;
    if (formattedArgs) {
      fullPath += '?' + formattedArgs;
    }
    return fullPath;
  }

  static async load(playlistId) {
    const playlistItemsUrl = YoutubePlaylistBlog.getUrl('https://www.googleapis.com/youtube/v3/playlistItems',
    {
      playlistId: playlistId,
      maxResults: 50,
      part: 'snippet',
      key: YoutubeKey,
    });
    const playlistUrl = YoutubePlaylistBlog.getUrl('https://www.googleapis.com/youtube/v3/playlists',
    {
      id: playlistId,
      part: 'snippet',
      key: YoutubeKey,
    });
    const playlistItemsResult = await (await fetch(playlistItemsUrl)).json();
    const playlistResult = await (await fetch(playlistUrl)).json();
    return new YoutubePlaylistBlog(playlistResult, playlistItemsResult);
  }
}
