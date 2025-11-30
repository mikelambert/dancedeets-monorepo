/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import {
  FlatList,
  ListRenderItemInfo,
  StyleSheet,
  TouchableHighlight,
  View,
} from 'react-native';
import { WebView } from 'react-native-webview';
import YouTube from 'react-native-youtube';
import { Text } from '../ui';
import { getRemoteBlogs } from './liveLearnConfig';
import { BlogPost, Blog, FeedBlog, MediumBlog, YoutubePlaylistBlog } from './models';

type Post = any;

interface BlogPostContentsProps {
  post: Post;
}

export class BlogPostContents extends React.Component<BlogPostContentsProps> {
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
        <WebView
          source={{ uri: this.props.post.url }}
          style={styles.listView}
        />
      );
    }
  }
}

interface BlogPostTitleProps {
  onPress: (post: Post) => void;
  post: Post;
}

export class BlogPostTitle extends React.Component<BlogPostTitleProps> {
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

interface BlogPostProps {
  blog: Blog;
  onSelected: (post: BlogPost) => void;
}

export class BlogPostList extends React.Component<BlogPostProps> {
  renderItem = ({ item }: ListRenderItemInfo<Post>) => {
    return <BlogPostTitle post={item} onPress={this.props.onSelected} />;
  };

  keyExtractor = (item: Post, index: number): string => {
    return item.url || String(index);
  };

  render() {
    return (
      <FlatList
        data={this.props.blog.posts}
        renderItem={this.renderItem}
        keyExtractor={this.keyExtractor}
      />
    );
  }
}

interface BlogTitleProps {
  onPress: (blog: Blog) => void;
  blog: Blog;
}

class BlogTitle extends React.Component<BlogTitleProps> {
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

interface BlogProps {
  onSelected: (blog: Blog) => void;
}

interface BlogListState {
  blogs: Blog[];
}

export class BlogList extends React.Component<BlogProps, BlogListState> {
  constructor(props: BlogProps) {
    super(props);
    this.state = { blogs: [] };
  }

  componentDidMount() {
    this.loadFeeds();
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
          return null;
        }
      })
    );
    const filteredBlogData = blogData.filter((x): x is Blog => x !== null);
    this.setState({ blogs: filteredBlogData });
  }

  renderItem = ({ item }: ListRenderItemInfo<Blog>) => {
    return <BlogTitle blog={item} onPress={this.props.onSelected} />;
  };

  keyExtractor = (item: Blog, index: number): string => {
    return item.title || String(index);
  };

  render() {
    return (
      <FlatList
        style={styles.listView}
        data={this.state.blogs}
        renderItem={this.renderItem}
        keyExtractor={this.keyExtractor}
        initialNumToRender={10}
        maxToRenderPerBatch={5}
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
