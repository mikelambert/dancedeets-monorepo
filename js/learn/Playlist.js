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
  HorizontalView,
  Text,
} from '../ui';
import { getRemoteTutorials } from '../learn/learnConfig';
import { Tutorial, Video } from './models';
import { yellowColors, purpleColors } from '../Colors';

export class TutorialListView extends React.Component {
  state: {
    tutorials: [Tutorial];
  };

  constructor(props) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    this.state = {
      tutorials: [],
    };
    this.load();
  }

  async load() {
    const tutorialsJson = await getRemoteTutorials();
    const tutorials = tutorialsJson.map((x) => new Tutorial(x));
    this.setState({tutorials: tutorials});
  }

  renderRow(tutorial: Tutorial) {
    const duration = formatDuration(tutorial.getDurationSeconds());
    return <TouchableHighlight onPress={() => {
      this.props.onSelected(tutorial);
    }}>
      <View style={{margin: 7}}>
        <Text style={styles.text}>{tutorial.title}</Text>
        <Text style={styles.text}>{tutorial.author}</Text>
        <Text style={styles.text}>{duration}</Text>
      </View>
    </TouchableHighlight>;
  }

  render() {
    return <FeedListView
      items={this.state.tutorials}
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

export class TutorialView extends React.Component {
  youtubePlayer: any;

  constructor(props) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).renderHeader = this.renderHeader.bind(this);
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
        // Hacks because of how the imperative API works
        this.youtubePlayer.setNativeProps({
          videoId: video.youtubeId,
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

  render() {
    // TODO: fix videoID on the main youtube docs?
    // also explain setNativeProps
    // push up our fixes?
    //
    // for my client feature-bar (if i support scrub bar):
    // speed-rate, play/pause, back-ten-seconds, airplay
    return <View style={styles.container}>
      <YouTube
        ref={(x) => {
          this.youtubePlayer = x;
        }}
        videoId={this.props.tutorial.sections[0].videos[0].youtubeId}
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
    backgroundColor: 'white',
  },
  text: {
    color: 'white',
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
