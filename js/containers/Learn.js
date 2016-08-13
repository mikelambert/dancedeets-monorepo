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

class BlogPostList extends React.Component {
  state: {
    dataSource: ListView.DataSource,
  };

  constructor(props) {
    super(props);
    var dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
    });
    this.state = {dataSource};
    (this: any)._renderRow = this._renderRow.bind(this);
  }

  _getNewState(posts) {
    const results = posts || [];
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRows(results),
    };
    return state;
  }

  async loadFeeds() {
    const blogs = await getRemoteBlogs();
    const blogData = await Promise.all(blogs.map((x) => getMediumFeed(x)));
    this.setState(this._getNewState(blogData[0]));
  }

  componentWillMount() {
    this.loadFeeds();
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

export default class LearnApp extends React.Component {

  render() {
    return <View style={styles.container}>
      <BlogPostList />
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
