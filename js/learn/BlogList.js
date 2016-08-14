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
} from 'react-native';
import {
  Text,
} from '../ui';
import {
  getRemoteBlogs
} from './learnConfig';

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
  authorLookup: { [key: string]: string };
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

type Props = {};

export default class BlogList extends React.Component {
  state: {
    blogs: [MediumFeed];
  };

  constructor(props: Props) {
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

const styles = StyleSheet.create({
  listView: {
    flex: 1,
  },
});
