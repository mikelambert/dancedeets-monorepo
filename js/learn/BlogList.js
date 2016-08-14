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
import {
  getRemoteBlogs
} from './learnConfig';
import {
  BlogPost,
  MediumBlog,
} from './models';

export class BlogPostItem extends React.Component {
  render() {
    return <Text>{this.props.post.title}</Text>;
  }
}

type BlogPostProps = {
  blog: MediumBlog;
};

export class BlogPostList extends React.Component {
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

  _getNewState(blog: MediumBlog) {
    const results = blog.posts || [];
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRows(results),
    };
    return state;
  }

  _renderRow(post: BlogPost) {
    return <BlogPostItem
      post={post}
      //onEventClicked={(post: BlogPost) => {this.props.clickEvent(post);}}
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

export class BlogList extends React.Component {
  state: {
    blogs: [MediumBlog];
  };

  constructor(props: Props) {
    super(props);
    this.state = {blogs: []};
  }

  async loadFeeds() {
    const blogs = await getRemoteBlogs();
    const blogData = await Promise.all(blogs.map((x) => MediumBlog.load(x)));
    this.setState({blogs: blogData});
  }

  componentWillMount() {
    this.loadFeeds();
  }

  render() {
    if (!this.state.blogs.length) {
      return <View style={styles.listView} />;
    }
    return <BlogPostList blog={this.state.blogs[0]} />;
  }
}

const styles = StyleSheet.create({
  listView: {
    flex: 1,
    backgroundColor: '#000',
  },
});
