/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Image,
  ListView,
  StyleSheet,
  TouchableHighlight,
  View,
} from 'react-native';
import { track } from '../store/track';
import YouTube from 'react-native-youtube';
import { FeedListView } from './BlogList';
import {
  Card,
  HorizontalView,
  ProportionalImage,
  Text,
} from '../ui';
import { getRemoteTutorials } from '../learn/liveLearnConfig';
import { Tutorial, Video } from './models';
import { purpleColors } from '../Colors';
import shallowEqual from 'fbjs/lib/shallowEqual';
import styleEqual from 'style-equal';


export class TutorialStylesView extends React.Component {
  state: {
    styleTutorials: {[style: string]: [Tutorial]};
  };

  constructor(props) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    this.state = {
      styleTutorials: {},
    };
    this.load();
  }

  async load() {
    const tutorialsJson = await getRemoteTutorials();

    const styleTutorials = {};
    Object.keys(tutorialsJson).forEach((style) => {
      styleTutorials[style] = tutorialsJson[style].map((x) => new Tutorial(x));
    });
    this.setState({styleTutorials: styleTutorials});
  }

  renderRow(style: string) {
    // When we have per-style images
    // <Image source={{uri: style}} style={styles.thumbnail} />
    const tutorials = this.state.styleTutorials[style];
    const thumbnails = tutorials.map((tutorial) =>
      <Image source={{uri: tutorial.thumbnail}} style={styles.miniThumbnail} />
    );
    const groupedThumbnails = [];
    let i = 0;
    while (i < thumbnails.length) {
      groupedThumbnails.push(
        <HorizontalView key={i} style={{flex: 1}}>
          {thumbnails[i] ? thumbnails[i] : null}
          {thumbnails[i + 1] ? thumbnails[i + 1] : null}
          {thumbnails[i + 2] ? thumbnails[i + 2] : null}
        </HorizontalView>
      );
      i += 3;
    }
    return <TouchableHighlight
      onPress={() => {
        this.props.onSelected(style, this.state.styleTutorials[style]);
      }}>
      <Card
        title={
          <Text style={[styles.text, styles.tutorialTitle, styles.tutorialListRow]}>{style}</Text>
        }>
        <View style={{margin: 7}}>
          <Text style={styles.text}>{this.state.styleTutorials[style].length} Tutorials</Text>
          {groupedThumbnails}
        </View>
      </Card>
    </TouchableHighlight>;
  }

  render() {
    return <FeedListView
      items={Object.keys(this.state.styleTutorials)}
      renderRow={this.renderRow}
      />;
  }
}

export class TutorialListView extends React.Component {
  constructor(props) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderRow(tutorial: Tutorial) {
    const duration = formatDuration(tutorial.getDurationSeconds());
    return <TouchableHighlight
      onPress={() => {
        this.props.onSelected(tutorial);
      }}>
      <Card
        title={
          <Text style={[styles.text, styles.tutorialTitle, styles.tutorialListRow]}>{tutorial.title}</Text>
        }>
        <View style={{margin: 7}}>
          <Image source={{uri: tutorial.thumbnail}} style={styles.thumbnail} />
          <Text style={styles.text}>Teacher: {tutorial.author}</Text>
          <Text style={styles.text}>Duration: {duration}</Text>
        </View>
      </Card>
    </TouchableHighlight>;
  }

  render() {
    return <FeedListView
      items={this.props.tutorials}
      renderRow={this.renderRow}
      />;
  }
}

function formatDuration(durationSeconds: number) {
  const hours = Math.floor(durationSeconds / 60 / 60);
  const minutes = Math.floor(durationSeconds / 60) % 60;
  const seconds = durationSeconds % 60;
  const minutesString = (hours && minutes < 10) ? '0' + minutes : minutes;
  const secondsString = (seconds < 10) ? '0' + seconds : seconds;
  if (durationSeconds > 60 * 60) {
    return `${hours}:${minutesString}:${secondsString}`;
  } else {
    return `${minutesString}:${secondsString}`;
  }
}

type FeedProps = {
  items: {[key: any]: any};
  sectionHeaders: [any];
  renderRow: (row: any) => any;
  renderSectionHeader: (header: any) => any;
  renderHeader: ?() => any;
};

export class SectionedListView extends React.Component {
  state: {
    dataSource: ListView.DataSource,
  };
  props: FeedProps;

  constructor(props: FeedProps) {
    super(props);
    var dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
      sectionHeaderHasChanged: (s1, s2) => s1 !== s2,
    });
    this.state = {dataSource};
    this.state = this._getNewState(this.props.items, this.props.sectionHeaders);
  }

  _getNewState(items: {[key: any]: any}, sectionHeaders: [any]) {
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRowsAndSections(items, sectionHeaders),
    };
    return state;
  }

  componentWillReceiveProps(nextProps: FeedProps) {
    this.setState(this._getNewState(nextProps.items, nextProps.sectionHeaders));
  }

  render() {
    return <ListView
      style={[styles.listView]}
      dataSource={this.state.dataSource}
      renderRow={this.props.renderRow}
      renderHeader={this.props.renderHeader}
      renderSectionHeader={this.props.renderSectionHeader}
      initialListSize={10}
      pageSize={5}
      scrollRenderAheadDistance={10000}
      indicatorStyle="white"
     />;
  }
}

// This is a wrapper around <YouTube> that ignores any changes to the videoId,
// and instead uses them to update the YouTube object directly.
class YouTubeNoReload extends React.Component {
  _root: React.Component;

  shouldComponentUpdate(nextProps, nextState) {
    const style = this.props.style;
    const nextStyle = nextProps.style;
    const trimmedProps = {...this.props, style: null, videoId: null};
    const trimmedNextProps = {...nextProps, style: null, videoId: null};
    const diff = !styleEqual(style, nextStyle) || !shallowEqual(trimmedProps, trimmedNextProps) || !shallowEqual(this.state, nextState);
    if (!diff && (this.props.videoId != nextProps.videoId)) {
      this._root.setNativeProps({
        videoId: nextProps.videoId,
        play: false,
      });
      this._root.setNativeProps({
        play: true,
      });
    }
    return diff;
  }

  setNativeProps(props) {
    this._root.setNativeProps(props);
  }

  render() {
    return <YouTube
      ref={(x) => {
        this._root = x;
      }}
      {...this.props}
      />;
  }
}

export class TutorialView extends React.Component {
  youtubePlayer: any;

  state: {
    selectedIndex: number;
  };

  constructor(props) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).renderHeader = this.renderHeader.bind(this);
    this.state = {
      selectedIndex: 0,
    };
  }

  renderHeader() {
    const description = this.props.tutorial.description ? <Text style={[styles.text, styles.tutorialDescription]}>{this.props.tutorial.description}</Text> : null;
    const duration = formatDuration(this.props.tutorial.getDurationSeconds());
    return <View style={styles.tutorialRow}>
      <Text style={[styles.text, styles.tutorialTitle]}>{this.props.tutorial.title}</Text>
      {description}
      <Text style={[styles.text, styles.tutorialSubtitle]}>{this.props.tutorial.author} - {duration}</Text>
    </View>;
  }

  renderRow(video: any) {
    const duration = formatDuration(video.getDurationSeconds());
    return <TouchableHighlight
      underlayColor={purpleColors[0]}
      activeOpacity={0.5}
      onPress={() => {
        // TODO: Track post details
        track('Blog Post Selected');
        const index = this.props.tutorial.getVideoIndex(video);
        //TODO: Enable this to make setState work.
        // It unfortunately causes a html-video-reload, which ends up being slower
        // than reusing the existing video object and just setting the video id.
        this.setState({selectedIndex: index});

        //navigatable.onNavigate({key: 'BlogPostItem', title: post.title, post: post});
      }}>
      <View>
      <HorizontalView style={styles.videoRow}>
        <Image source={require('./images/play.png')} style={styles.videoPlay} />
        <View style={{flex: 1}}>
          <Text style={[styles.text, styles.videoTitle]}>{video.title}</Text>
          <Text style={[styles.text, styles.videoDuration]}>{duration}</Text>
        </View>
      </HorizontalView>
      </View>
    </TouchableHighlight>;

  }

  renderSectionHeader(data: [Video], sectionId: string) {
    const sectionData = JSON.parse(sectionId);
    const duration = formatDuration(sectionData.durationSeconds);
    return <View style={styles.sectionRow}>
      <Text style={[styles.text, styles.sectionTitle]}>{sectionData.index + 1} - {sectionData.title}</Text>
      <Text style={[styles.text, styles.sectionDuration]}>{duration}</Text>
    </View>;
  }

  getSelectedVideo() {
    return this.props.tutorial.getVideo(this.state.selectedIndex);
  }

  render() {
    // TODO: fix videoID on the main youtube docs?
    // also explain setNativeProps
    // push up our fixes?
    //
    // for my client feature-bar (if i support scrub bar):
    // speed-rate, play/pause, back-ten-seconds, airplay
    return <View style={styles.container}>
      <YouTubeNoReload
        ref={(x) => {
          this.youtubePlayer = x;
        }}
        videoId={this.getSelectedVideo(this.state.selectedIndex).youtubeId}
        play={false}
        hidden={false}
        playsInline={true}
        loop={false}
        rel={false}
        showinfo={true}
        //controls={0}
        modestbranding={true}
        style={{alignSelf: 'stretch', height: 220, backgroundColor: 'black'}}
        />
      <SectionedListView
        items={this.props.tutorial.getItems()}
        sectionHeaders={this.props.tutorial.getSectionHeaders()}
        renderRow={this.renderRow}
        renderSectionHeader={this.renderSectionHeader}
        renderHeader={this.renderHeader}
        />
    </View>;
  }
}

let styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
  },
  text: {
    color: 'white',
  },
  miniThumbnail: {
    height: 50,
    flex: 1,
  },
  thumbnail: {
    borderRadius: 10,
    height: 200,
  },
  tutorialListRow: {
    padding: 7,
  },
  tutorialRow: {
    padding: 7,
    backgroundColor: purpleColors[4],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderColor: purpleColors[3],
  },
  tutorialTitle: {
    fontWeight: 'bold',
    fontSize: 18,
    lineHeight: 20,
  },
  tutorialSubtitle: {
    fontSize: 15,
    lineHeight: 18,
  },
  sectionRow: {
    padding: 7,
    backgroundColor: purpleColors[4],
  },
  sectionTitle: {
    fontSize: 15,
    lineHeight: 18,
  },
  sectionDuration: {
    color: '#ccc',
    fontSize: 12,
    lineHeight: 15,
  },
  videoRow: {
    alignItems: 'center',
    padding: 7,
    backgroundColor: purpleColors[3],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderColor: purpleColors[4],
  },
  videoTitle: {
    fontWeight: 'bold',
    fontSize: 15,
    lineHeight: 18,
  },
  videoDuration: {
    color: '#ccc',
    fontSize: 12,
    lineHeight: 15,
  },
  videoPlay: {
    width: 25,
    height: 25,
    marginRight: 5,
  },
});
