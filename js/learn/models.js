/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { feed } from '../api/dancedeets';
import moment from 'moment';

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

export class Tutorial {
  title: string;
  description: string;
  author: string;
  style: string;
  language: string;
  thumbnail: string;
  sections: [Section];

  constructor(json: any) {
    this.title = json.title;
    this.description = json.description;
    this.author = json.author;
    this.style = json.style;
    this.language = json.language;
    this.thumbnail = json.thumbnail;
    this.sections = json.sections.map((x) => new Section(x));
  }
  getDurationSeconds(): number {
    return this.sections.reduce((reduced, item) => reduced + item.getDurationSeconds(), 0);
  }

  getItems() {
    const items = {};
    this.sections.forEach((x, i) => {
      items[x.key(i)] = x.videos;
    });
    return items;
  }

  getSectionHeaders() {
    return this.sections.map((x, i) => x.key(i));
  }

  getVideo(index: number) {
    const originalIndex = index;
    for (var i = 0; i < this.sections.length; i++) {
      const section = this.sections[i];
      if (index < section.videos.length) {
        return section.videos[index];
      } else {
        index -= section.videos.length;
      }
    }
    console.error(`Video index out of range: ${originalIndex}`);
  }

  getVideoIndex(video: Video) {
    let index = 0;
    for (var i = 0; i < this.sections.length; i++) {
      const videos = this.sections[i].videos;
      const sectionIndex = videos.indexOf(video);
      if (sectionIndex > -1) {
        return index + sectionIndex;
      } else {
        index += videos.length;
      }
    }
    console.error('Video not in tutorial for index lookup');
  }
}

export class Section {
  title: string;
  videos: [Video];

  constructor(json: any) {
    console.log(json);
    this.title = json.title;
    this.videos = json.videos.map((x) => new Video(x));
  }

  getDurationSeconds(): number {
    return this.videos.reduce((reduced, item) => reduced + item.getDurationSeconds(), 0);
  }

  key(index: number) {
    return JSON.stringify({
      index: index,
      title: this.title,
      durationSeconds: this.getDurationSeconds(),
    });
  }
}

export class Video {
  title: string;
  duration: number;
  url: string;
  youtubeId: string;

  constructor(json: any) {
    this.title = json.title;
    this.duration = json.duration;
    this.youtubeId = json.youtubeId;
  }

  getDurationSeconds(): number {
    return moment.duration(this.duration).asSeconds();
  }
}

export class YoutubeTutorial extends Tutorial {
}

export function createYoutubeTutorial(json: any) {

}

export class YoutubePlaylistBlog extends Blog {
  constructor(playlistJson: any, playlistItemsJson: any, videosJson: any) {
    super();
    this.title = playlistJson.items[0].snippet.title;
    this.description = playlistJson.items[0].snippet.description;
    this.url = `https://www.youtube.com/playlist?list=${playlistJson.items[0].id}`;

    const contentDetailsLookup = {};
    videosJson.items.forEach((x) => {
      contentDetailsLookup[x.id] = x.contentDetails;
    });
    // Filter out any private/deleted videos which we can't access contentDetails for
    const filteredPlaylistItems = playlistItemsJson.items
      .filter((x) => contentDetailsLookup[x.snippet.resourceId.videoId]);

    this.posts = filteredPlaylistItems.map((x) => this.parsePlaylistItem(x.snippet, contentDetailsLookup[x.snippet.resourceId.videoId]));
  }

  author() {
    //TODO: Fix this!
    return this.posts[0].author;
  }

  durationSeconds() {
    return this.posts.reduce((prev, current) => prev + current.durationSeconds, 0);
  }

  parsePlaylistItem(snippet: any, contentDetails: any): BlogPost {
    return {
      title: snippet.title,
      preview: snippet.description,
      postTime: snippet.publishedAt,
      author: snippet.channelTitle,
      url: `https://www.youtube.com/watch?v=${snippet.resourceId.videoId}`,
      youtubeId: snippet.resourceId.videoId,
      durationSeconds: moment.duration(contentDetails.duration).asSeconds(),
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

  static async getTimes(playlistItemsJson) {
    const videoIds = playlistItemsJson.items.map((x) => x.snippet.resourceId.videoId);
    const playlistItemsUrl = YoutubePlaylistBlog.getUrl('https://www.googleapis.com/youtube/v3/videos',
    {
      id: videoIds.join(','),
      maxResults: 50,
      part: 'contentDetails',
      key: YoutubeKey,
    });
    const videosResult = await (await fetch(playlistItemsUrl)).json();
    return videosResult;
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
    const videosResult = await YoutubePlaylistBlog.getTimes(playlistItemsResult);
    const playlistResult = await (await fetch(playlistUrl)).json();
    return new YoutubePlaylistBlog(playlistResult, playlistItemsResult, videosResult);
  }
}
