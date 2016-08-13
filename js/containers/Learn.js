/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  ListView,
  RefreshControl,
  StyleSheet,
  View,
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
  url: string;
};

class MediumFeed {
  title: string;
  description: string;
  url: string;
  authorLookup: [];
  posts: [Post];

  constructor(json) {
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

  parseMediumPost(realPost): Post {
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
    return new MediumFeed(json);
  }
}

class BlogPost extends React.Component {
  render() {
    return <Text>{this.props.post.title}</Text>;
  }
}

type BlogPostProps = {
  blog: MediumFeed;
};

class BlogPostList extends React.Component {
  state: {
    dataSource: ListView.DataSource,
  };
  props: BlogPostProps;

  constructor(props) {
    super(props);
    var dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
    });
    this.state = {dataSource};
    this.state = this._getNewState(this.props.blog);
    (this: any)._renderRow = this._renderRow.bind(this);
  }

  _getNewState(blog: MediumFeed) {
    const results = blog.posts || [];
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRows(results),
    };
    return state;
  }

  _renderRow(post: Post) {
    return <BlogPost
      post={post}
      //onEventClicked={(post: Post) => {this.props.clickEvent(post);}}
    />;
  }

  render() {
    return <ListView
      style={[styles.listView]}
      dataSource={this.state.dataSource}
      refreshControl={
        <RefreshControl
          refreshing={false}
          //refreshing={are-we-refreshing?}
          //onRefresh={() => this.props.reloadAddEvents()}
        />
      }
      renderRow={this._renderRow}
      initialListSize={10}
      pageSize={5}
      scrollRenderAheadDistance={10000}
      scrollsToTop={false}
      indicatorStyle="white"
     />;
  }
}

class BlogList extends React.Component {
  state: {
    blogs: [MediumFeed];
  };

  constructor(props) {
    super(props);
    this.state = {blogs: []};
  }

  async loadFeeds() {
    const blogs = await getRemoteBlogs();
    const blogData = await Promise.all(blogs.map((x) => MediumFeed.load(x)));
    this.setState({blogs: blogData});
  }

  componentWillMount() {
    this.loadFeeds();
  }

  render() {
    if (!this.state.blogs.length) {
      return null;
    }
    return <BlogPostList blog={this.state.blogs[0]} />;
  }
}

export default class LearnApp extends React.Component {

  render() {
    return <View style={styles.container}>
      <BlogList />
    </View>;
  }
}


const styles = StyleSheet.create({
  container: {
    //top: STATUSBAR_HEIGHT,
    flex: 1,
    backgroundColor: 'black',
  },
  listView: {
    flex: 1,
  },
});
