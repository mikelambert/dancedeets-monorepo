/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Image,
  StyleSheet,
  TouchableHighlight,
  View,
} from 'react-native';
import { track } from '../store/track';
import YouTube from 'react-native-youtube';
import { FeedListView } from './BlogList';
import {
  HorizontalView,
  Text,
} from '../ui';

export class VideoList extends React.Component {
  youtubePlayer: any;

  constructor(props) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderRow(post: any) {
    const duration = `${Math.floor(post.durationSeconds / 60)}:${post.durationSeconds % 60}`;
    return <TouchableHighlight onPress={() => {
      // TODO: Track post details
      track('Blog Post Selected');
      // Hacks because of how the imperative API works
      this.youtubePlayer.setNativeProps({
        videoId: post.youtubeId,
        play: false,
      });
      this.youtubePlayer.setNativeProps({
        play: true,
      });
      //navigatable.onNavigate({key: 'BlogPostItem', title: post.title, post: post});
    }}>
    <View>
    <HorizontalView style={styles.videoRow}>
      <Image source={require('./images/play.png')} style={styles.videoPlay} />
      <View style={{flex: 1}}>
        <Text style={styles.videoTitle}>{post.title}</Text>
        <Text style={styles.videoDuration}>{duration}</Text>
      </View>
    </HorizontalView>
    </View>
    </TouchableHighlight>;

  }

  render() {
    return <View style={styles.container}>
      <YouTube
        ref={(x) => {
          this.youtubePlayer = x;
        }}
        videoId={this.props.playlist.posts[0].youtubeId}
        play={false}
        hidden={false}
        playsInline={true}
        loop={false}
        rel={false}
        showinfo={true}
        modestbranding={true}
        style={{alignSelf: 'stretch', height: 220, backgroundColor: 'black'}}
        />
      <FeedListView
        items={this.props.playlist.posts}
        renderRow={this.renderRow}
        />
    </View>;
  }
}

let styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  videoRow: {
    alignItems: 'center',
    margin: 7,
  },
  videoTitle: {
    fontWeight: 'bold',
    fontSize: 15,
    lineHeight: 18,
  },
  videoDuration: {
    fontSize: 12,
    lineHeight: 15,
  },
  videoPlay: {
    width: 25,
    height: 25,
    marginRight: 5,
  },
});
