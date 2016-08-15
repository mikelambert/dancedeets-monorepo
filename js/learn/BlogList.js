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
  TouchableHighlight,
  View,
} from 'react-native';
import {
  Text,
} from '../ui';
import {
  getRemoteBlogs
} from './learnConfig';
import type {
  BlogPost,
} from './models';
import {
  Blog,
  MediumBlog,
  FeedBlog,
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

  constructor(props: BlogPostProps) {
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
      onEventClicked={(post: BlogPost) => {this.props.clickEvent(post);}}
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
      indicatorStyle="white"
     />;
  }
}

class BlogTitle extends React.Component {
  render() {
    return <TouchableHighlight onPress={() => {
      this.props.onPress(this.props.blog);
    }}>
      <View>
        <Text>{this.props.blog.title}</Text>
      </View>
    </TouchableHighlight>;
  }
}

type BlogProps = {
  blogs: [Blog];
  onSelected: (blog: Blog) => void;
};

export class BlogList extends React.Component {
  state: {
    dataSource: ListView.DataSource,
  };
  props: BlogProps;

  constructor(props: BlogProps) {
    super(props);
    var dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
    });
    this.state = {dataSource};
    this.state = this._getNewState(this.props.blogs);
    (this: any)._renderRow = this._renderRow.bind(this);
  }

  async loadFeeds() {
    const blogs = await getRemoteBlogs();
    const blogData = await Promise.all(blogs.map((x) => {
      if (x.indexOf('http') > -1) {
        return FeedBlog.load(x);
      } else {
        return MediumBlog.load(x);
      }
    }));
    this.setState(this._getNewState(blogData));
  }

  componentWillMount() {
    this.loadFeeds();
  }

  _getNewState(blogs: [Blog]) {
    const results = blogs || [];
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRows(results),
    };
    return state;
  }

  _renderRow(blog: Blog) {
    return <BlogTitle
      blog={blog}
      onPress={this.props.onSelected}
    />;
  }

  render() {
    return <ListView
      style={[styles.listView]}
      dataSource={this.state.dataSource}
      renderRow={this._renderRow}
      initialListSize={10}
      pageSize={5}
      scrollRenderAheadDistance={10000}
      indicatorStyle="white"
     />;
  }
}

const styles = StyleSheet.create({
  listView: {
    flex: 1,
    backgroundColor: '#000',
  },
});
