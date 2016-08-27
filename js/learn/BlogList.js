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
} from './liveLearnConfig';
import type {
  Blog,
  BlogPost,
  FeedBlog,
  MediumBlog,
  YoutubePlaylistBlog,
} from './models';
import WKWebView from 'react-native-wkwebview';
import YouTube from 'react-native-youtube';

export class BlogPostContents extends React.Component {
  render() {
    if (this.props.post.youtubeId) {
      return <YouTube
        ref="youtubePlayer"
        videoId={this.props.post.youtubeId}
        play={true}
        hidden={true}
        playsInline={true}
        loop={false}
        style={{alignSelf: 'stretch', height: 300}}
        />;
    } else {
      return <WKWebView
        source={{uri: this.props.post.url}}
        style={styles.listView}
        />;
    }
  }
}

export class BlogPostTitle extends React.Component {
  render() {
    return <TouchableHighlight onPress={() => {
      this.props.onPress(this.props.post);
    }}>
      <View>
        <Text style={styles.text}>{this.props.post.title}</Text>
        <Text style={styles.text}>{this.props.post.author}</Text>
      </View>
    </TouchableHighlight>;
  }
}

type FeedProps = {
  items: [any];
  renderRow: (post: BlogPost) => any;
  renderHeader: ?() => any;
};

export class FeedListView extends React.Component {
  state: {
    dataSource: ListView.DataSource,
  };

  constructor(props: FeedProps) {
    super(props);
    var dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
    });
    this.state = {dataSource};
    this.state = this._getNewState(this.props.items);
  }

  _getNewState(items: [any]) {
    const results = items || [];
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRows(results),
    };
    return state;
  }

  componentWillReceiveProps(nextProps: FeedProps) {
    this.setState(this._getNewState(nextProps.items));
  }

  render() {
    return <ListView
      style={[styles.listView]}
      dataSource={this.state.dataSource}
      renderRow={this.props.renderRow}
      renderHeader={this.props.renderHeader}
      initialListSize={10}
      pageSize={5}
      scrollRenderAheadDistance={10000}
      indicatorStyle="white"
     />;
  }
}

type BlogPostProps = {
  blog: Blog;
  onSelected: (post: BlogPost) => void;
};

export class BlogPostList extends React.Component {

  constructor(props: BlogPostProps) {
    super(props);
    (this: any)._renderRow = this._renderRow.bind(this);
  }

  _renderRow(post: BlogPost) {
    return <BlogPostTitle
      post={post}
      onPress={this.props.onSelected}
    />;
  }

  render() {
    return <FeedListView
      items={this.props.blog.posts}
      renderRow={this._renderRow}
      />;
  }
}

class BlogTitle extends React.Component {
  render() {
    return <TouchableHighlight onPress={() => {
      this.props.onPress(this.props.blog);
    }}>
      <View style={{margin: 7}}>
        <Text style={styles.text}>{this.props.blog.title}</Text>
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
    const blogData = await Promise.all(blogs.map(async (x) => {
      try {
        if (x.indexOf('http') > -1) {
          return await FeedBlog.load(x);
        } else if (x.indexOf('y:') > -1) {
          return await YoutubePlaylistBlog.load(x.substr(2));
        } else {
          return await MediumBlog.load(x);
        }
      } catch (e) {
        console.error(`Error opening ${x}: ${e}`);
        return new Promise((resolve, reject) => resolve());
      }
    }));
    const filteredBlogData = blogData.filter((x) => x);
    this.setState(this._getNewState(filteredBlogData));
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
    backgroundColor: 'black',
  },
  text: {
    color: 'white',
  }
});
