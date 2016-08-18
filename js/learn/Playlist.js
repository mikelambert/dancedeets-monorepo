/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  TouchableHighlight,
  View,
} from 'react-native';
import { track } from '../store/track';
import YouTube from 'react-native-youtube';
import { FeedListView } from './BlogList';
import {
  Text,
} from '../ui';

export class VideoList extends React.Component {
  youtubePlayer: any;

  constructor(props) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderRow(post: any) {
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
        <Text>{post.title}</Text>
        <Text>{post.author}</Text>
        <Text>{post.durationSeconds} seconds</Text>
      </View>
    </TouchableHighlight>;

  }

  render() {
    return <View>
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
