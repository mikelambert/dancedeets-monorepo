/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  AlertIOS,
  Dimensions,
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
  Button,
  HorizontalView,
  Text,
} from '../ui';
import { getRemoteTutorials } from './liveLearnConfig';
import { Playlist, Video } from './playlistModels';
import { purpleColors } from '../Colors';
import shallowEqual from 'fbjs/lib/shallowEqual';
import styleEqual from 'style-equal';
import {
  injectIntl,
} from 'react-intl';
import languages from '../languages';
const Mailer = require('NativeModules').RNMail;

type PlaylistStylesViewProps = {
  onSelected: (playlist: Playlist) => void;
};

const boxWidth = 150;
const boxMargin = 5;

function listViewWidth() {
  const fullBox = boxWidth + boxMargin;
  return Math.floor(Dimensions.get('window').width / fullBox) * fullBox - 20;
}

function sortedTutorials(tutorials, language) {
  const nativeTutorials = [];
  const foreignTutorials = [];
  tutorials.forEach((tut) => {
    if (tut.language == language) {
      nativeTutorials.push(tut);
    } else {
      foreignTutorials.push(tut);
    }
  });
  return [].concat(nativeTutorials, foreignTutorials);
}

class _PlaylistStylesView extends React.Component {
  state: {
    stylePlaylists: [any];
  };

  constructor(props: PlaylistStylesViewProps) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    this.state = {
      stylePlaylists: [],
    };
    this.load();
  }

  async load() {
    const playlistsJson = await getRemoteTutorials();

    const constructedPlaylists = playlistsJson.map((style) => {
      return {
        ...style,
        tutorials: sortedTutorials(style.tutorials, this.props.intl.locale).map((x) => new Playlist(x)),
      };
    });
    this.setState({stylePlaylists: constructedPlaylists});
  }

  renderRow(style: any) {
    return <TouchableHighlight
      onPress={() => {
        this.props.onSelected(style, this.state.stylePlaylists[style]);
      }}
      >
      <View style={{
        width: boxWidth,
        margin: boxMargin,
        padding: 5,
        backgroundColor: purpleColors[2],
        borderRadius: 10,
        alignItems: 'center',
      }}>
        <Image source={style.thumbnail} resizeMode="contain" style={{width: 120, height: 120}}/>
        <Text style={{fontWeight: 'bold'}}>{style.title}</Text>
        <Text>{style.tutorials.length} Tutorials</Text>
      </View>
    </TouchableHighlight>;
  }

  renderHeader() {
    return <Text style={{
      textAlign: 'center',
      margin: 10,
      width: listViewWidth(),
    }}>Choose a style you'd like to learn:</Text>;
  }

  render() {
    return <FeedListView
      items={this.state.stylePlaylists}
      renderRow={this.renderRow}
      renderHeader={this.renderHeader}
      contentContainerStyle={{
        alignSelf: 'center',
        justifyContent: 'flex-start',
        flexDirection: 'row',
        flexWrap: 'wrap',
        alignItems: 'flex-start',
      }}
      />;
  }
}
export const PlaylistStylesView = injectIntl(_PlaylistStylesView);

type PlaylistListViewProps = {
  onSelected: (playlist: Playlist) => void;
  playlists: [Playlist];
};

class _PlaylistListView extends React.Component {
  constructor(props: PlaylistListViewProps) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderRow(playlist: Playlist) {
    const duration = formatDuration(playlist.getDurationSeconds());
    let title = playlist.title;
    if (this.props.intl.locale != playlist.language) {
      const localizedLanguage = languages[this.props.intl.locale][playlist.language];
      title = `${localizedLanguage}: ${playlist.title}`;
    }
    return <TouchableHighlight
      onPress={() => {
        this.props.onSelected(playlist);
      }}
      >
      <View
        style={{
          width: boxWidth,
          backgroundColor: purpleColors[2],
          margin: boxMargin,
          padding: 5,
          borderRadius: 10,
        }}>
        <Image source={{uri: playlist.thumbnail}} resizeMode="cover" style={styles.thumbnail} />
        <Text style={{fontWeight: 'bold'}}>{title}</Text>
        <Text>{playlist.getVideoCount()} videos: {duration}</Text>
      </View>
    </TouchableHighlight>;
  }

  renderHeader() {
    return <Text style={{
      textAlign: 'center',
      margin: 10,
      width: listViewWidth(),
    }}>Choose a tutorial:</Text>;
  }

  renderFooter() {
    return <View style={{
        margin: 10,
        width: listViewWidth(),
      }}>
      <Text>
      Want to list your tutorials, DVD, or classes?{"\n"}
      Want to progress beyond these tutorials?{"\n"}
      Want exclusive tutorials from the world's best dancers?{"\n"}
      </Text>
      <HorizontalView style={{alignItems: 'center'}}>
      <Text>Then </Text>
      <Button
        size="small"
        caption="Contact Us"
        onPress={this.sendTutorialContactEmail}
      >Contact Us</Button>
      <Text> and let us know!</Text>
      </HorizontalView>
    </View>;
  }

  sendTutorialContactEmail() {
    track('Contact Tutorials');
    Mailer.mail({
        subject: 'More Tutorials',
        recipients: ['advertising@dancedeets.com'],
        body: '',
      }, (error, event) => {
          if (error) {
            AlertIOS.alert('Error', 'Please email us at feedback@dancedeets.com');
          }
      });
  }

  render() {
    return <FeedListView
      items={this.props.playlists}
      renderRow={this.renderRow}
      renderHeader={this.renderHeader}
      renderFooter={this.renderFooter}
      contentContainerStyle={{
        alignSelf: 'center',
        justifyContent: 'flex-start',
        flexDirection: 'row',
        flexWrap: 'wrap',
        alignItems: 'flex-start',
      }}
      />;
  }
}
export const PlaylistListView = injectIntl(_PlaylistListView);

function formatDuration(durationSeconds: number) {
  const hours = Math.floor(durationSeconds / 60 / 60);
  const minutes = Math.floor(durationSeconds / 60) % 60;
  if (durationSeconds > 60 * 60) {
    return `${hours}h ${minutes}m`;
  } else if (durationSeconds > 60) {
    return `${minutes}m`;
  } else {
    return `${durationSeconds}s`;
  }
}

type SectionedListViewProps = {
  items: {[key: any]: any};
  sectionHeaders: [any];
  renderRow: (row: any) => any;
  renderSectionHeader: (data: [any], sectionId: string) => any;
  renderHeader: ?() => any;
};

export class SectionedListView extends React.Component {
  state: {
    dataSource: ListView.DataSource,
  };

  constructor(props: SectionedListViewProps) {
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

  componentWillReceiveProps(nextProps: SectionedListViewProps) {
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
  _root: any;

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

type PlaylistViewProps = {
  playlist: Playlist;
};

export class PlaylistView extends React.Component {
  youtubePlayer: any;

  state: {
    selectedIndex: number;
  };

  constructor(props: PlaylistViewProps) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).renderHeader = this.renderHeader.bind(this);
    (this: any).renderSectionHeader = this.renderSectionHeader.bind(this);
    this.state = {
      selectedIndex: 0,
    };
  }

  renderHeader() {
    const subtitle = this.props.playlist.subtitle ? <Text style={styles.playlistSubtitle}>{this.props.playlist.subtitle}</Text> : null;
    const duration = formatDuration(this.props.playlist.getDurationSeconds());
    return <View style={styles.playlistRow}>
      <Text style={styles.playlistTitle}>{this.props.playlist.title}</Text>
      {subtitle}
      <Text style={styles.playlistSubtitle}>{this.props.playlist.author} - {duration}</Text>
    </View>;
  }

  renderRow(video: any) {
    const duration = formatDuration(video.getDurationSeconds());
    return <TouchableHighlight
      underlayColor={purpleColors[0]}
      activeOpacity={0.5}
      onPress={() => {
        const index = this.props.playlist.getVideoIndex(video);

        track('Tutorial Video Selected', {
          tutorialName: this.props.playlist.title,
          tutorialStyle: this.props.playlist.style,
          tutorialVideoIndex: index,
        });

        //TODO: Enable this to make setState work.
        // It unfortunately causes a html-video-reload, which ends up being slower
        // than reusing the existing video object and just setting the video id.
        this.setState({selectedIndex: index});
      }}>
      <View>
      <HorizontalView style={styles.videoRow}>
        <Image source={require('./images/play.png')} style={styles.videoPlay} />
        <View style={{flex: 1}}>
          <Text style={styles.videoTitle}>{video.title}</Text>
          <Text style={styles.videoDuration}>{duration}</Text>
        </View>
      </HorizontalView>
      </View>
    </TouchableHighlight>;

  }

  renderSectionHeader(data: [Video], sectionId: string) {
    // If there's only one section, let's ignore showing the section header.
    // It's just confusing relative to the real header.
    if (this.props.playlist.getSectionHeaders().length === 1) {
      return null;
    }
    const sectionData = JSON.parse(sectionId);
    const duration = formatDuration(sectionData.durationSeconds);
    return <View style={styles.sectionRow}>
      <Text style={styles.sectionTitle}>{sectionData.index + 1} - {sectionData.title}</Text>
      <Text style={styles.sectionDuration}>{duration}</Text>
    </View>;
  }

  getSelectedVideo() {
    return this.props.playlist.getVideo(this.state.selectedIndex);
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
        items={this.props.playlist.getItems()}
        sectionHeaders={this.props.playlist.getSectionHeaders()}
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
  miniThumbnail: {
    height: 50,
    flex: 1,
  },
  thumbnail: {
    borderRadius: 10,
    height: 100,
  },
  playlistListRow: {
    padding: 7,
  },
  playlistRow: {
    padding: 7,
    backgroundColor: purpleColors[4],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderColor: purpleColors[3],
  },
  playlistTitle: {
    fontWeight: 'bold',
    fontSize: 18,
    lineHeight: 20,
  },
  playlistSubtitle: {
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
