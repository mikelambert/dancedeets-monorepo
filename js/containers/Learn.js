/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  ScrollView,
  StyleSheet,
} from 'react-native';
import {
  Text,
} from '../ui';
import { RemoteConfig } from 'react-native-firebase3';

const defaultBlogs = [
  'rue-magazine',
];

const defaultTutorials = [];

async function loadConfig() {
  RemoteConfig.setNamespacedDefaults({
    blogs: JSON.stringify(defaultBlogs),
    tutorials: JSON.stringify(defaultTutorials),
  }, 'Learn');
  await RemoteConfig.fetchWithExpirationDuration(30 * 15);
  await RemoteConfig.activateFetched();
}

loadConfig();

async function getRemoteBlogs() {
  return JSON.parse(await RemoteConfig.getNamedspacedString('blogs', 'Learn'));
}

type Post = {
  title: string;
  preview: string;
  postTime: number;
  author: string;
};

function parseMediumPost(realPost, authorLookup): Post {
  return {
    title: realPost.title,
    preview: realPost.virtuals.snippet,
    postTime: realPost.createdAt,
    author: authorLookup[realPost.creatorId],
  };
}

async function getMediumFeed(name) {
  const feedName = `https://medium.com/${name}?format=json`;
  const result = await fetch(feedName);
  const fullText = await result.text();
  const text = fullText.substring(fullText.indexOf('{'));
  const json = JSON.parse(text);
  return processMediumFeed(json);
}

function processMediumFeed(json) {
  const realPosts: [any] = Object.values(json.payload.references.Post);
  const users = json.payload.references.User;
  const authorLookup = Object.keys(users).reduce(function(previous, x) {
    previous[x] = users[x].name;
    return previous;
  }, {});
  const posts: [Post] = realPosts.map((x) => parseMediumPost(x, authorLookup));
  return posts;
}


class BlogPost extends React.Component {
  render() {
    return <Text>{this.props.post.title}</Text>;
  }
}

type Props = {};

export default class LearnApp extends React.Component {

  constructor(props: Props) {
    super(props);
    this.state = {
      feeds: [],
    };
  }

  state: {
    feeds: [[Post]];
  };

  async loadFeeds() {
    const blogs = await getRemoteBlogs();
    const blogData = await Promise.all(blogs.map((x) => getMediumFeed(x)));
    this.setState({feeds: blogData});
  }

  componentWillMount() {
    this.loadFeeds();
  }

  render() {
    if (!this.state.feeds.length) {
      return null;
    }
    const posts = this.state.feeds[0].map((x: Post) => <BlogPost key={x.title} post={x} />);
    return <ScrollView style={styles.container} contentContainerStyle={styles.containerContent}>
      {posts}
    </ScrollView>;
  }
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
  },
  containerContent: {
    //top: STATUSBAR_HEIGHT,
    backgroundColor: 'black',
    alignItems: 'center',
    justifyContent: 'space-around',
  },
});
