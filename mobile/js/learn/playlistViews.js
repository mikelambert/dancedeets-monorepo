/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  AlertIOS,
  Dimensions,
  Image,
  ListView,
  Platform,
  StyleSheet,
  TouchableHighlight,
  View,
} from 'react-native';
import {
  injectIntl,
  intlShape,
} from 'react-intl';
import { connect } from 'react-redux';
import YouTube from 'react-native-youtube';
import shallowEqual from 'fbjs/lib/shallowEqual';
import styleEqual from 'style-equal';
import upperFirst from 'lodash/upperFirst';
import type { Style } from 'dancedeets-common/js/styles';
import { Playlist, Video } from 'dancedeets-common/js/tutorials/models';
import styleIcons from 'dancedeets-common/js/styles/icons';
import { getTutorials } from 'dancedeets-common/js/tutorials/playlistConfig';
import messages from 'dancedeets-common/js/tutorials/messages';
import languages from 'dancedeets-common/js/languages';
import {
  formatDuration,
} from 'dancedeets-common/js/tutorials/format';
import { track } from '../store/track';
import { FeedListView } from './BlogList';
import {
  Button,
  HorizontalView,
  Text,
} from '../ui';
import { purpleColors } from '../Colors';
import {
  semiNormalize,
  normalize,
} from '../ui/normalize';
import type { Dispatch } from '../actions/types';
import {
  setTutorialVideoIndex,
} from '../actions';
import { googleKey } from '../keys';
import sendMail from '../util/sendMail';

type PlaylistStylesViewProps = {
  onSelected: (playlist: Playlist) => void;
};

// Try to make our boxes as wide as we can...
let boxWidth = normalize(170);
// ...and only start scaling them non-proportionally on the larger screen sizes,
// so that we do 3-4 columns
if (Dimensions.get('window').width >= 1024) {
  boxWidth = semiNormalize(170);
}
const boxMargin = 5;

function listViewWidth() {
  const fullBox = boxWidth + boxMargin;
  return Math.floor((Dimensions.get('window').width / fullBox) * fullBox) - 10;
}

class _PlaylistStylesView extends React.Component {
  props: {
    onSelected: (style: Style, playlists: Array<Playlist>) => void;

    // Self-managed props
    intl: intlShape;
  }

  state: {
    stylePlaylists: [];
  }

  constructor(props: PlaylistStylesViewProps) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).renderHeader = this.renderHeader.bind(this);
    this.state = {
      stylePlaylists: getTutorials(this.props.intl.locale),
    };
  }

  renderRow(category: any) {
    const imageWidth = boxWidth - 30;
    const durationSeconds = category.tutorials.reduce((prev, current) => prev + current.getDurationSeconds(), 0);
    const length = formatDuration(this.props.intl.formatMessage, durationSeconds);
    let styleTitle = category.style.title;
    if (category.style.titleMessage) {
      styleTitle = this.props.intl.formatMessage(category.style.titleMessage);
    }
    return (<TouchableHighlight
      onPress={() => {
        this.props.onSelected(category, this.state.stylePlaylists[category]);
      }}
      style={{
        margin: boxMargin,
        borderRadius: 10,
      }}
    >
      <View
        style={{
          width: boxWidth,
          padding: 5,
          backgroundColor: purpleColors[2],
          borderRadius: 10,
          alignItems: 'center',
        }}
      >
        <Image source={styleIcons[category.style.id]} resizeMode="contain" style={{ width: imageWidth, height: imageWidth }} />
        <Text style={[styles.boxTitle, styles.boxText]}>{styleTitle}</Text>
        <Text style={styles.boxText}>{this.props.intl.formatMessage(messages.numTutorials, { count: category.tutorials.length })}</Text>
        <Text style={styles.boxText}>{this.props.intl.formatMessage(messages.totalTime, { time: length })}</Text>
      </View>
    </TouchableHighlight>);
  }

  renderHeader() {
    return (<Text
      style={{
        textAlign: 'center',
        margin: 10,
        width: listViewWidth(),
      }}
    >{this.props.intl.formatMessage(messages.chooseStyle)}</Text>);
  }

  render() {
    return (<FeedListView
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
    />);
  }
}
export const PlaylistStylesView = injectIntl(_PlaylistStylesView);

type PlaylistListViewProps = {
  onSelected: (playlist: Playlist) => void;
  playlists: Array<Playlist>;
};

class _PlaylistListView extends React.Component {
  props: {
    playlists: Array<Playlist>;
    onSelected: (playlist: Playlist) => void;

    // Self-managed props
    intl: intlShape;
  }

  constructor(props: PlaylistListViewProps) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).renderHeader = this.renderHeader.bind(this);
    (this: any).renderFooter = this.renderFooter.bind(this);
  }

  sendTutorialContactEmail() {
    track('Contact Tutorials');
    sendMail({
      subject: 'More Tutorials',
      to: 'advertising@dancedeets.com',
      body: '',
    });
  }

  renderRow(playlist: Playlist) {
    const duration = formatDuration(this.props.intl.formatMessage, playlist.getDurationSeconds());
    let title = playlist.title;
    if (this.props.intl.locale !== playlist.language) {
      const localizedLanguage = languages[this.props.intl.locale][playlist.language];
      title = this.props.intl.formatMessage(messages.languagePrefixedTitle, { language: upperFirst(localizedLanguage), title: playlist.title });
    }
    const numVideosDuration = this.props.intl.formatMessage(messages.numVideosWithDuration, { count: playlist.getVideoCount(), duration });
    return (<TouchableHighlight
      onPress={() => {
        this.props.onSelected(playlist);
      }}
      style={{
        margin: boxMargin,
        borderRadius: 10,
      }}
    >
      <View
        style={{
          width: boxWidth,
          backgroundColor: purpleColors[2],
          padding: 5,
          borderRadius: 10,
        }}
      >
        <Image source={{ uri: playlist.thumbnail }} resizeMode="cover" style={styles.thumbnail} />
        <Text style={[styles.boxTitle, styles.boxText]}>{title}</Text>
        <Text style={styles.boxText}>{numVideosDuration}</Text>
      </View>
    </TouchableHighlight>);
  }

  renderHeader() {
    return (<Text
      style={{
        textAlign: 'center',
        margin: 10,
        width: listViewWidth(),
      }}
    >{this.props.intl.formatMessage(messages.chooseTutorial)}</Text>);
  }

  renderFooter() {
    return (<View
      style={{
        margin: 10,
        width: listViewWidth(),
      }}
    >
      <Text>
        {this.props.intl.formatMessage(messages.tutorialFooter)}
      </Text>
      <HorizontalView style={{ alignItems: 'center' }}>
        <Button
          size="small"
          caption={this.props.intl.formatMessage(messages.contact)}
          onPress={this.sendTutorialContactEmail}
        >Contact Us</Button>{' '}
        <Text>{this.props.intl.formatMessage(messages.contactSuffix)}</Text>
      </HorizontalView>
    </View>);
  }

  render() {
    return (<FeedListView
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
    />);
  }
}
export const PlaylistListView = injectIntl(_PlaylistListView);

type SectionedListViewProps = {
  items: {[key: any]: any};
  sectionHeaders: [];
};

export class SectionedListView extends React.Component {
  state: {
    dataSource: ListView.DataSource,
  };

  _listView: ListView;

  constructor(props: SectionedListViewProps) {
    super(props);
    const dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
      sectionHeaderHasChanged: (s1, s2) => s1 !== s2,
    });
    this.state = { dataSource };
    this.state = this.getNewState(this.props.items, this.props.sectionHeaders);
  }

  componentWillReceiveProps(nextProps: SectionedListViewProps) {
    this.setState(this.getNewState(nextProps.items, nextProps.sectionHeaders));
  }

  getNewState(items: {[key: any]: any}, sectionHeaders: []) {
    const state = {
      ...this.state,
      dataSource: this.state.dataSource.cloneWithRowsAndSections(items, sectionHeaders),
    };
    return state;
  }

  scrollTo(options: {x?: number; y?: number; animated?: boolean}) {
    this._listView.scrollTo(options);
  }

  render() {
    const { sectionHeaders, items, ...otherProps } = this.props;
    return (<ListView
      ref={(x) => { this._listView = x; }}
      dataSource={this.state.dataSource}
      initialListSize={10}
      pageSize={5}
      scrollRenderAheadDistance={10000}
      indicatorStyle="white"
      {...otherProps}
    />);
  }
}

// This is a wrapper around <YouTube> that ignores any changes to the videoId,
// and instead uses them to update the YouTube object directly.
class YouTubeNoReload extends React.Component {
  props: {
    style: View.propTypes.style;
    videoId: string;
  }
  _root: any;

  shouldComponentUpdate(nextProps, nextState) {
    if (Platform.OS === 'ios') {
      return true;
    }
    const style = this.props.style;
    const nextStyle = nextProps.style;
    const trimmedProps = { ...this.props, style: null, videoId: null };
    const trimmedNextProps = { ...nextProps, style: null, videoId: null };
    const diff = !styleEqual(style, nextStyle) || !shallowEqual(trimmedProps, trimmedNextProps) || !shallowEqual(this.state, nextState);
    if (!diff && (this.props.videoId !== nextProps.videoId)) {
      // setNativeProps only exists on Android, be careful!
      this.setNativeProps({
        videoId: nextProps.videoId,
        play: false,
      });
      this.setNativeProps({
        play: true,
      });
    }
    return diff;
  }

  setNativeProps(props) {
    this._root.setNativeProps(props);
  }

  render() {
    return (<YouTube
      ref={(x) => {
        this._root = x;
      }}
      {...this.props}
    />);
  }
}

type PlaylistViewProps = {
  playlist: Playlist;
};

class _PlaylistView extends React.Component {
  _youtubePlayer: YouTubeNoReload;
  _sectionedListView: SectionedListView;
  _cachedLayout: Array<Array<{top: number, bottom: number}>>;
  _viewDimensions: {top: number, bottom: number};

  constructor(props: PlaylistViewProps) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).renderHeader = this.renderHeader.bind(this);
    (this: any).renderSectionHeader = this.renderSectionHeader.bind(this);
    (this: any).onChangeState = this.onChangeState.bind(this);
    (this: any).onListViewLayout = this.onListViewLayout.bind(this);
    (this: any).onListViewScroll = this.onListViewScroll.bind(this);
    this._cachedLayout = [];
  }

  componentWillReceiveProps(nextProps: any) {
    if (nextProps.selectedTab !== 'learn') {
      this._youtubePlayer.setNativeProps({
        play: false,
      });
    }
  }

  componentWillUnmount() {
    // So the next time we open up a playlist, it will start at the beginning
    this.props.setTutorialVideoIndex(0);
  }

  onListViewScroll(e) {
    const top = e.nativeEvent.contentOffset.y;
    const bottom = top + e.nativeEvent.layoutMeasurement.height;
    this._viewDimensions = { top, bottom };
  }

  onChangeState(props: Object) {
    if (props.state === 'ended') {
      // next video, if we're not at the end!
      const newIndex = this.props.tutorialVideoIndex + 1;
      if (newIndex < this.props.playlist.getVideoCount()) {
        // scroll it into view
        this.ensureTutorialVisible(newIndex);
        // and select it, playing the video
        this.props.setTutorialVideoIndex(newIndex);
      }
    }
  }

  onListViewLayout(e) {
    const top = e.nativeEvent.layout.y;
    const bottom = top + e.nativeEvent.layout.height;
    this._viewDimensions = { top, bottom };
  }

  getSelectedVideo() {
    return this.props.playlist.getVideo(this.props.tutorialVideoIndex);
  }

  setCachedLayoutForRow(section, row, top, bottom) {
    if (!this._cachedLayout[section]) {
      this._cachedLayout[section] = [];
    }
    this._cachedLayout[section][row] = { top, bottom };
  }

  ensureTutorialVisible(index) {
    const { section, row } = this.props.playlist.getVideoSectionRow(index);
    // {top, bottom} of the element
    const element = this._cachedLayout[section][row];
    // {top, bottom} of the containing view's current scroll position
    const view = this._viewDimensions;

    let newScroll = null;
    // if we're off the bottom of the screen
    if (element.bottom > view.bottom) {
      // figure out the proper scroll amount to fit it on the screen
      newScroll = view.top + (element.bottom - view.bottom);
    }
    // or if we're off the top of the screen
    if (element.top < view.top) {
      // ensure we stick it at the top
      newScroll = element.top;
    }
    // only scroll if necessary
    if (newScroll !== null) {
      this._sectionedListView.scrollTo({
        y: newScroll,
        animated: true,
      });
    }
  }


  renderHeader() {
    const subtitle = this.props.playlist.subtitle ? <Text style={styles.playlistSubtitle}>{this.props.playlist.subtitle}</Text> : null;
    const duration = formatDuration(this.props.intl.formatMessage, this.props.playlist.getDurationSeconds());
    return (<View style={styles.playlistRow}>
      <Text style={styles.playlistTitle}>{this.props.playlist.title}</Text>
      {subtitle}
      <Text style={styles.playlistSubtitle}>{this.props.playlist.author} - {duration}</Text>
    </View>);
  }

  renderRow(rowData: any, section: string, row: string) {
    const { video, selected } = rowData;
    const duration = formatDuration(this.props.intl.formatMessage, video.getDurationSeconds());
    const sectionIndex = this.props.playlist.getSectionHeaders().indexOf(section);
    return (<TouchableHighlight
      underlayColor={purpleColors[0]}
      activeOpacity={0.5}
      onPress={() => {
        const index = this.props.playlist.getVideoIndex(video);

        track('Tutorial Video Selected', {
          tutorialName: this.props.playlist.title,
          tutorialStyle: this.props.playlist.style,
          tutorialVideoIndex: index,
        });

        this.props.setTutorialVideoIndex(index);
      }}
      onLayout={(e) => {
        const rowIndex = parseInt(row, 10);
        const top = e.nativeEvent.layout.y;
        const bottom = top + e.nativeEvent.layout.height;
        this.setCachedLayoutForRow(sectionIndex, rowIndex, top, bottom);
      }}
    >
      <View>
        <HorizontalView style={[styles.videoRow, selected ? styles.videoActiveRow : styles.videoInactiveRow]}>
          <Image source={require('./images/play.png')} style={styles.videoPlay} />
          <View style={{ flex: 1 }}>
            <Text style={styles.videoTitle}>{video.title}</Text>
            <Text style={styles.videoDuration}>{duration}</Text>
          </View>
        </HorizontalView>
      </View>
    </TouchableHighlight>);
  }

  renderSectionHeader(data: Video[], sectionId: string) {
    // If there's only one section, let's ignore showing the section header.
    // It's just confusing relative to the real header.
    if (this.props.playlist.getSectionHeaders().length === 1) {
      return null;
    }
    const sectionData = JSON.parse(sectionId);
    const duration = formatDuration(this.props.intl.formatMessage, sectionData.durationSeconds);
    return (<View style={styles.sectionRow}>
      <Text style={styles.sectionTitle}>{sectionData.title}</Text>
      <Text style={styles.sectionDuration}>{duration}</Text>
    </View>);
  }

  render() {
    // TODO: fix videoID on the main youtube docs?
    // also explain setNativeProps
    // push up our fixes?
    //
    // for my client feature-bar (if i support scrub bar):
    // speed-rate, play/pause, back-ten-seconds, airplay
    const video = this.getSelectedVideo();
    const height = (Dimensions.get('window').width * video.height) / video.width;
    return (<View style={styles.container}>
      <YouTubeNoReload
        ref={(x) => {
          this._youtubePlayer = x;
        }}
        apiKey={googleKey}
        videoId={video.youtubeId}
        play // auto-play when loading a tutorial
        hidden={false}
        playsInline
        loop={false}
        rel={false}
        showinfo
        // controls={0}
        modestbranding
        style={{ alignSelf: 'stretch', height }}
        onChangeState={this.onChangeState}
      />
      <View style={styles.listViewWrapper}>
        <SectionedListView
          ref={(x) => {
            this._sectionedListView = x;
          }}
          items={this.props.playlist.getItems(this.props.tutorialVideoIndex)}
          sectionHeaders={this.props.playlist.getSectionHeaders()}
          renderRow={this.renderRow}
          renderSectionHeader={this.renderSectionHeader}
          renderHeader={this.renderHeader}
          onScroll={this.onListViewScroll}
          onLayout={this.onListViewLayout}
        />
      </View>
    </View>);
  }
}
export const PlaylistView = connect(
  state => ({
    tutorialVideoIndex: state.tutorials.videoIndex,
    selectedTab: state.mainTabs.selectedTab,
  }),
  (dispatch: Dispatch) => ({
    setTutorialVideoIndex: (eventId, language) => dispatch(setTutorialVideoIndex(eventId, language)),
  }),
)(injectIntl(_PlaylistView));

let styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  miniThumbnail: {
    height: 50,
    flex: 1,
  },
  thumbnail: {
    borderRadius: 10,
    height: semiNormalize(100),
  },
  listViewWrapper: {
    flex: 1,
    borderTopWidth: 1,
  },
  boxTitle: {
    fontWeight: 'bold',
  },
  boxText: {
    fontSize: semiNormalize(14),
    lineHeight: normalize(22),
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
    fontSize: semiNormalize(18),
    lineHeight: semiNormalize(20),
  },
  playlistSubtitle: {
    fontSize: semiNormalize(15),
    lineHeight: semiNormalize(18),
  },
  sectionRow: {
    padding: 7,
    backgroundColor: purpleColors[4],
  },
  sectionTitle: {
    fontSize: semiNormalize(15),
    lineHeight: semiNormalize(18),
  },
  sectionDuration: {
    color: '#ccc',
    fontSize: semiNormalize(12),
    lineHeight: semiNormalize(15),
  },
  videoRow: {
    alignItems: 'center',
    padding: 7,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderColor: purpleColors[4],
  },
  videoActiveRow: {
    backgroundColor: purpleColors[0],
  },
  videoInactiveRow: {
    backgroundColor: purpleColors[3],
  },
  videoTitle: {
    fontWeight: 'bold',
    fontSize: semiNormalize(15),
    lineHeight: semiNormalize(18),
  },
  videoDuration: {
    color: '#ccc',
    fontSize: semiNormalize(12),
    lineHeight: semiNormalize(15),
  },
  videoPlay: {
    width: semiNormalize(25),
    height: semiNormalize(25),
    marginRight: 5,
  },
});
