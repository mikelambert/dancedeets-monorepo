/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import {
  FlatList,
  ListView,
  StyleSheet,
  TouchableHighlight,
  View,
} from 'react-native';
import WKWebView from 'react-native-wkwebview-reborn';
import YouTube from 'react-native-youtube';
import { Text } from '../ui';
import { getRemoteBlogs } from './liveLearnConfig';
import type { BlogPost } from './models';
import { Blog, FeedBlog, MediumBlog, YoutubePlaylistBlog } from './models';

type Post = any;

export class BlogPostContents extends React.Component<{
  post: Post,
}> {
  render() {
    if (this.props.post.youtubeId) {
      return (
        <YouTube
          videoId={this.props.post.youtubeId}
          play
          hidden
          loop={false}
          style={{ alignSelf: 'stretch', height: 300 }}
        />
      );
    } else {
      return (
        <WKWebView
          source={{ uri: this.props.post.url }}
          style={styles.listView}
        />
      );
    }
  }
}

export class BlogPostTitle extends React.Component<{
  onPress: (post: Post) => void,
  post: Post,
}> {
  render() {
    return (
      <TouchableHighlight
        onPress={() => {
          this.props.onPress(this.props.post);
        }}
      >
        <View>
          <Text style={styles.text}>{this.props.post.title}</Text>
          <Text style={styles.text}>{this.props.post.author}</Text>
        </View>
      </TouchableHighlight>
    );
  }
}

type BlogPostProps = {
  blog: Blog,
  onSelected: (post: BlogPost) => void,
};

export class BlogPostList extends React.Component<BlogPostProps> {
  constructor(props: BlogPostProps) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderRow(row: { item: Post }) {
    const post = row.item;
    return <BlogPostTitle post={post} onPress={this.props.onSelected} />;
  }

  render() {
    return (
      <FlatList data={this.props.blog.posts} renderItem={this.renderRow} />
    );
  }
}

class BlogTitle extends React.Component<{
  onPress: (blog: Blog) => void,
  blog: Blog,
}> {
  render() {
    return (
      <TouchableHighlight
        onPress={() => {
          this.props.onPress(this.props.blog);
        }}
      >
        <View style={{ margin: 7 }}>
          <Text style={styles.text}>{this.props.blog.title}</Text>
        </View>
      </TouchableHighlight>
    );
  }
}

type BlogProps = {
  onSelected: (blog: Blog) => void,
};

export class BlogList extends React.Component<
  BlogProps,
  {
    dataSource: ListView.DataSource,
  }
> {
  constructor(props: BlogProps) {
    super(props);
    const dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
    });
    this.state = { dataSource };
    // We don't take in any props.blogs, so no need to run this:
    // this.state = this.getNewState(this.props.blogs);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  componentWillMount() {
    this.loadFeeds();
  }

  getNewState(blogs: Blog[]) {
    const results = blogs || [];
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRows(results),
    };
    return state;
  }

  async loadFeeds() {
    const blogs = await getRemoteBlogs();
    const blogData = await Promise.all(
      blogs.map(async x => {
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
      })
    );
    const filteredBlogData = blogData.filter(x => x);
    this.setState(this.getNewState(filteredBlogData));
  }

  renderRow(blog: Blog) {
    return <BlogTitle blog={blog} onPress={this.props.onSelected} />;
  }

  render() {
    return (
      <ListView
        style={[styles.listView]}
        dataSource={this.state.dataSource}
        renderRow={this.renderRow}
        initialListSize={10}
        pageSize={5}
        scrollRenderAheadDistance={10000}
        indicatorStyle="white"
      />
    );
  }
}

const styles = StyleSheet.create({
  listView: {
    flex: 1,
  },
  text: {
    color: 'white',
  },
});
