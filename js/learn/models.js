/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { feed } from '../api/dancedeets';

export type BlogPost = {
  title: string;
  preview: string;
  postTime: number;
  author: string;
  url: string;
};

class Blog {
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
    this.title = json.title;
    this.description = json.subtitle;
    this.url = json.link;
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
    console.log(json);
    return new FeedBlog(json);
  }
}
