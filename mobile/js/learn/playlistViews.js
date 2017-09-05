/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  AlertIOS,
  Animated,
  Dimensions,
  FlatList,
  Image,
  Platform,
  SectionList,
  StyleSheet,
  TouchableHighlight,
  TouchableOpacity,
  View,
} from 'react-native';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import { connect } from 'react-redux';
import shallowEqual from 'fbjs/lib/shallowEqual';
import styleEqual from 'style-equal';
import upperFirst from 'lodash/upperFirst';
import VideoPlayer from './VideoPlayer';
import Icon from 'react-native-vector-icons/FontAwesome';
import type { Style } from 'dancedeets-common/js/styles';
import { Playlist } from 'dancedeets-common/js/tutorials/models';
import styleIcons from 'dancedeets-common/js/styles/icons';
import { getTutorials } from 'dancedeets-common/js/tutorials/playlistConfig';
import type { Category } from 'dancedeets-common/js/tutorials/playlistConfig';
import messages from 'dancedeets-common/js/tutorials/messages';
import languages from 'dancedeets-common/js/languages';
import { formatDuration } from 'dancedeets-common/js/tutorials/format';
import { track } from '../store/track';
import { Button, DarkText, HorizontalView, Text } from '../ui';
import { purpleColors } from '../Colors';
import { semiNormalize, normalize } from '../ui/normalize';
import type { Dispatch } from '../actions/types';
import { setTutorialVideoIndex } from '../actions';
import sendMail from '../util/sendMail';
import getYoutubeInfo from '../api/youtubeVideoInfo';

type PlaylistStylesViewProps = {
  onSelected: (playlist: Playlist) => void,
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
  return Math.floor(Dimensions.get('window').width / fullBox * fullBox) - 10;
}

class _PlaylistStylesView extends React.Component {
  props: {
    onSelected: (category: Category) => void,

    // Self-managed props
    intl: intlShape,
  };

  state: {
    stylePlaylists: Array<Category>,
  };

  constructor(props) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).renderHeader = this.renderHeader.bind(this);
    this.state = {
      stylePlaylists: getTutorials(this.props.intl.locale).map(x => ({
        ...x,
        key: x.style.id,
      })),
    };
  }

  renderRow(row) {
    const category = row.item;
    const imageWidth = boxWidth - 30;
    const durationSeconds = category.tutorials.reduce(
      (prev, current) => prev + current.getDurationSeconds(),
      0
    );
    const length = formatDuration(
      this.props.intl.formatMessage,
      durationSeconds
    );
    let styleTitle = category.style.title;
    if (category.style.titleMessage) {
      styleTitle = this.props.intl.formatMessage(category.style.titleMessage);
    }
    return (
      <TouchableOpacity
        onPress={() => {
          this.props.onSelected(category);
        }}
        style={{
          margin: boxMargin,
        }}
      >
        <View
          style={{
            width: boxWidth,
            padding: 5,
            alignItems: 'center',
          }}
        >
          <Image
            source={styleIcons[category.style.id]}
            resizeMode="contain"
            style={[
              styles.shadowed,
              {
                width: imageWidth,
                height: imageWidth,
              },
            ]}
          />
          <DarkText style={[styles.boxTitle, styles.boxText]}>
            {styleTitle}
          </DarkText>
          <DarkText style={styles.boxText}>
            {this.props.intl.formatMessage(messages.numTutorials, {
              count: category.tutorials.length,
            })}
          </DarkText>
          <DarkText style={styles.boxText}>
            {this.props.intl.formatMessage(messages.totalTime, {
              time: length,
            })}
          </DarkText>
        </View>
      </TouchableOpacity>
    );
  }

  renderHeader() {
    return (
      <DarkText
        style={{
          textAlign: 'center',
          margin: 10,
          width: listViewWidth(),
        }}
      >
        {this.props.intl.formatMessage(messages.chooseStyle)}
      </DarkText>
    );
  }

  render() {
    return (
      <FlatList
        data={this.state.stylePlaylists}
        renderItem={this.renderRow}
        renderHeader={this.renderHeader}
        contentContainerStyle={{
          alignSelf: 'center',
          justifyContent: 'flex-start',
          flexDirection: 'row',
          flexWrap: 'wrap',
          alignItems: 'flex-start',
        }}
      />
    );
  }
}
export const PlaylistStylesView = injectIntl(_PlaylistStylesView);

PlaylistStylesView.navigationOptions = ({ screenProps }) => ({
  title: screenProps.intl.formatMessage(messages.learnTitle),
});

type PlaylistListViewProps = {
  onSelected: (playlist: Playlist) => void,
  playlists: Array<Playlist>,
};

class _PlaylistListView extends React.Component {
  props: {
    playlists: Array<Playlist>,
    onSelected: (playlist: Playlist) => void,

    // Self-managed props
    intl: intlShape,
  };

  constructor(props) {
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

  renderRow(row) {
    const playlist = row.item;
    const duration = formatDuration(
      this.props.intl.formatMessage,
      playlist.getDurationSeconds()
    );
    let title = playlist.title;
    if (this.props.intl.locale !== playlist.language) {
      const localizedLanguage =
        languages[this.props.intl.locale][playlist.language];
      title = this.props.intl.formatMessage(messages.languagePrefixedTitle, {
        language: upperFirst(localizedLanguage),
        title: playlist.title,
      });
    }
    const numVideosDuration = this.props.intl.formatMessage(
      messages.numVideosWithDuration,
      { count: playlist.getVideoCount(), duration }
    );
    return (
      <TouchableOpacity
        onPress={() => {
          this.props.onSelected(playlist);
        }}
        style={{
          margin: boxMargin,
        }}
      >
        <View
          style={[
            {
              width: boxWidth,
              padding: 5,
              elevation: 5,
            },
            styles.shadowed,
          ]}
        >
          <Image
            source={{ uri: playlist.thumbnail }}
            resizeMode="cover"
            style={styles.thumbnail}
          />
          <DarkText style={[styles.boxTitle, styles.boxText]}>{title}</DarkText>
          <DarkText style={styles.boxText}>{numVideosDuration}</DarkText>
        </View>
      </TouchableOpacity>
    );
  }

  renderHeader() {
    return (
      <DarkText
        style={{
          textAlign: 'center',
          margin: 10,
          width: listViewWidth(),
        }}
      >
        {this.props.intl.formatMessage(messages.chooseTutorial)}
      </DarkText>
    );
  }

  renderFooter() {
    return (
      <View
        style={{
          margin: 10,
          width: listViewWidth(),
        }}
      >
        <DarkText>
          {this.props.intl.formatMessage(messages.tutorialFooter)}
        </DarkText>
        <HorizontalView style={{ alignItems: 'center' }}>
          <Button
            size="small"
            caption={this.props.intl.formatMessage(messages.contact)}
            onPress={this.sendTutorialContactEmail}
          >
            Contact Us
          </Button>
          <DarkText>
            {' '}
            {this.props.intl.formatMessage(messages.contactSuffix)}
          </DarkText>
        </HorizontalView>
      </View>
    );
  }

  render() {
    return (
      <FlatList
        data={this.props.playlists}
        renderItem={this.renderRow}
        renderHeader={this.renderHeader}
        renderFooter={this.renderFooter}
        contentContainerStyle={{
          alignSelf: 'center',
          justifyContent: 'flex-start',
          flexDirection: 'row',
          flexWrap: 'wrap',
          alignItems: 'flex-start',
        }}
      />
    );
  }
}
export const PlaylistListView = injectIntl(_PlaylistListView);

class _PlaylistView extends React.Component {
  props: {
    playlist: Playlist,
    tutorialVideoIndex: number,

    // Self-managed props
    intl: intlShape,
    setTutorialVideoIndex: (x: number) => void,
    mainScreenKey: string,
  };

  state: {
    isPlaying: boolean,
    onScreen: boolean,
    videoUrl: ?string,
  };

  _sectionedListView: SectionList<*>;
  _cachedLayout: Array<{ top: number, bottom: number }>;
  _viewDimensions: { top: number, bottom: number };

  constructor(props) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).renderHeader = this.renderHeader.bind(this);
    (this: any).renderSectionHeader = this.renderSectionHeader.bind(this);
    (this: any).onEnd = this.onEnd.bind(this);
    (this: any).onListViewLayout = this.onListViewLayout.bind(this);
    (this: any).onListViewScroll = this.onListViewScroll.bind(this);
    this._cachedLayout = [];
    this.state = { onScreen: true, isPlaying: true, videoUrl: null };
    this.updateFromProps(props);
  }

  updateFromProps(props) {
    if (
      !this.state.videoUrl ||
      this.props.tutorialVideoIndex != props.tutorialVideoIndex
    ) {
      const video = props.playlist.getVideo(props.tutorialVideoIndex);
      this.loadPlayerUrl(video);
    }
  }

  componentWillReceiveProps(nextProps) {
    this.setState({ onScreen: nextProps.mainScreenKey === 'Learn' });
    this.updateFromProps(nextProps);
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

  onError(event) {
    console.log('Youtube Error', event);
  }

  onEnd() {
    // next video, if we're not at the end!
    const newIndex = this.props.tutorialVideoIndex + 1;
    if (newIndex < this.props.playlist.getVideoCount()) {
      // scroll it into view
      this.ensureTutorialVisible(newIndex);
      // and select it, playing the video
      this.props.setTutorialVideoIndex(newIndex);
    }
  }

  onListViewLayout(e) {
    const top = e.nativeEvent.layout.y;
    const bottom = top + e.nativeEvent.layout.height;
    this._viewDimensions = { top, bottom };
  }

  setCachedLayoutForRow(index, top, bottom) {
    this._cachedLayout[index] = { top, bottom };
  }

  ensureTutorialVisible(index) {
    // {top, bottom} of the element
    const element = this._cachedLayout[index];
    // {top, bottom} of the containing view's current scroll position
    const view = this._viewDimensions;

    if (!view || !element) {
      console.error(`Ensuring Tutorial ${index} visible, but: `, {
        view,
        element,
      });
      return;
    }

    let viewPosition = null;
    // if we're off the bottom of the screen
    if (element.bottom > view.bottom) {
      // figure out the proper scroll amount to fit it on the screen
      viewPosition = 1;
    }
    // or if we're off the top of the screen
    if (element.top < view.top) {
      // ensure we stick it at the top
      viewPosition = 0;
    }
    // only scroll if necessary
    if (viewPosition !== null) {
      const { section, row } = this.props.playlist.getVideoSectionRow(index);
      this._sectionedListView.scrollToLocation({
        itemIndex: row,
        sectionIndex: section,
        animated: true,
        viewPosition,
      });
    }
  }

  renderHeader() {
    const subtitle = this.props.playlist.subtitle ? (
      <Text style={styles.playlistSubtitle}>
        {this.props.playlist.subtitle}
      </Text>
    ) : null;
    const duration = formatDuration(
      this.props.intl.formatMessage,
      this.props.playlist.getDurationSeconds()
    );
    return (
      <View style={styles.playlistRow}>
        <Text style={styles.playlistTitle}>{this.props.playlist.title}</Text>
        {subtitle}
        <Text style={styles.playlistSubtitle}>
          {this.props.playlist.author} - {duration}
        </Text>
      </View>
    );
  }

  renderRow({ item, section, index }) {
    const { video, selected } = item;
    const duration = formatDuration(
      this.props.intl.formatMessage,
      video.getDurationSeconds()
    );
    return (
      <TouchableHighlight
        underlayColor={purpleColors[0]}
        activeOpacity={0.5}
        onPress={() => {
          const videoIndex = this.props.playlist.getVideoIndex(video);
          if (videoIndex === this.props.tutorialVideoIndex) {
            this.setState({ isPlaying: !this.state.isPlaying });
          } else {
            track('Tutorial Video Selected', {
              tutorialName: this.props.playlist.title,
              tutorialStyle: this.props.playlist.style,
              tutorialVideoIndex: videoIndex,
            });

            this.setState({ isPlaying: true });
            this.props.setTutorialVideoIndex(videoIndex);
          }
        }}
        onLayout={e => {
          const top = e.nativeEvent.layout.y;
          const bottom = top + e.nativeEvent.layout.height;
          this.setCachedLayoutForRow(index, top, bottom);
        }}
      >
        <View>
          <HorizontalView
            style={[
              styles.videoRow,
              selected ? styles.videoActiveRow : styles.videoInactiveRow,
            ]}
          >
            <Icon
              name={
                this.state.isPlaying && selected ? (
                  'pause-circle'
                ) : (
                  'play-circle'
                )
              }
              size={20}
              style={styles.videoPlay}
              color="white"
            />
            <View style={{ flex: 1 }}>
              <Text style={styles.videoTitle}>{video.title}</Text>
              <Text style={styles.videoDuration}>{duration}</Text>
            </View>
          </HorizontalView>
        </View>
      </TouchableHighlight>
    );
  }

  renderSectionHeader({ section }) {
    // If there's only one section, let's ignore showing the section header.
    // It's just confusing relative to the real header.
    if (this.props.playlist.sections.length === 1) {
      return null;
    }
    const duration = formatDuration(
      this.props.intl.formatMessage,
      section.realSection.getDurationSeconds()
    );
    return (
      <View style={styles.sectionRow}>
        <Text style={styles.sectionTitle}>{section.title}</Text>
        <Text style={styles.sectionDuration}>{duration}</Text>
      </View>
    );
  }

  async loadPlayerUrl(video) {
    const youtubeInfo = await getYoutubeInfo(video.youtubeId);
    let videoData = youtubeInfo.formats.find(x => x.itag === '22');
    if (!videoData) {
      videoData = youtubeInfo.formats.find(x => x.itag === '18');
    }
    if (videoData) {
      this.setState({ videoUrl: videoData.url });
    }
  }

  render() {
    // for my client feature-bar (if i support scrub bar):
    // speed-rate, play/pause, back-ten-seconds, airplay
    const { videoUrl } = this.state;
    if (!videoUrl) {
      return null;
    }
    const video = this.props.playlist.getVideo(this.props.tutorialVideoIndex);
    const height = Dimensions.get('window').width * video.height / video.width;
    return (
      <View style={styles.container}>
        <VideoPlayer
          // Updating params
          source={{ uri: videoUrl }}
          paused={!this.state.isPlaying || !this.state.onScreen} // auto-play when loading a tutorial
          // Steady params
          controlTimeout={4000}
          loop={false}
          ignoreSilentSwitch="ignore"
          style={{ alignSelf: 'stretch', height }}
          // Callbacks
          onError={this.onError}
          onEnd={this.onEnd}
          onPlay={() => this.setState({ isPlaying: true })}
          onPause={() => {
            this.setState({ isPlaying: false });
          }}
        />
        <View style={styles.listViewWrapper}>
          <SectionList
            ref={x => {
              this._sectionedListView = x;
            }}
            sections={this.props.playlist.getSectionListData(
              this.props.tutorialVideoIndex
            )}
            renderItem={this.renderRow}
            renderSectionHeader={this.renderSectionHeader}
            renderHeader={this.renderHeader}
            stickySectionHeadersEnabled
            onScroll={this.onListViewScroll}
            onLayout={this.onListViewLayout}
          />
        </View>
      </View>
    );
  }
}
export const PlaylistView = connect(
  state => ({
    tutorialVideoIndex: state.tutorials.videoIndex,
    mainScreenKey: state.screens.routes[state.screens.index].key,
  }),
  (dispatch: Dispatch) => ({
    setTutorialVideoIndex: eventId => dispatch(setTutorialVideoIndex(eventId)),
  })
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
  shadowed: {
    shadowColor: 'black',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.4,
    shadowRadius: 10,
    overflow: 'visible', // Let the shadow bleed out on iOS
  },
  listViewWrapper: {
    flex: 1,
    borderTopWidth: 1,
    backgroundColor: 'black',
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
