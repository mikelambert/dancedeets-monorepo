/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Dimensions,
  Image,
  StyleSheet,
  View,
} from 'react-native';
import Carousel from 'react-native-carousel';
import LaunchScreen from './LaunchScreen';
import LinearGradient from 'react-native-linear-gradient';
import LoginButtonWithAlternate from './LoginButtonWithAlternate';
import {
  normalize,
  Text,
} from '../ui';
import {
  defineMessages,
  injectIntl,
} from 'react-intl';

var PAGES = [
  'Page 0',
  'Page 1',
  'Page 2',
  'Page 3',
];

const messages = defineMessages({
  'tutorial.0.header': {
    id: 'tutorial.0.header',
    defaultMessage: 'Take a Trip:',
    description: 'Intro screen header',
  },
  'tutorial.0.body': {
    id: 'tutorial.0.body',
    defaultMessage: 'Meet local dancers\nHit up dance events',
    description: 'Intro screen list of features',
  },
  'tutorial.1.header': {
    id: 'tutorial.1.header',
    defaultMessage: 'Learn to Dance:',
    description: 'Intro screen header',
  },
  'tutorial.1.body': {
    id: 'tutorial.1.body',
    defaultMessage: 'Take a class\nWatch a show\nHit the clubs',
    description: 'Intro screen list of features',
  },
  'tutorial.2.header': {
    id: 'tutorial.2.header',
    defaultMessage: 'Promote your event:',
    description: 'Intro screen header',
  },
  'tutorial.2.body': {
    id: 'tutorial.2.body',
    defaultMessage: 'Share your event\nShare your city\'s events\nReach dancers worldwide\nand join our 90,000 events',
    description: 'Intro screen list of features',
  },
  'nologin': {
    id: 'tutorial.nologin',
    defaultMessage: 'Don\'t want to login?',
    description: 'Link to a page for users who don\'t want to FB login',
  },
});

class _TopView extends React.Component {
  render() {
    const page = this.props.page;
    const header = this.props.intl.formatMessage(messages[`tutorial.${page}.header`]);
    const body = this.props.intl.formatMessage(messages[`tutorial.${page}.body`]);
    return (
      <View style={styles.centerItems} >
        <Text style={styles.onboardHeader}>{header.toUpperCase()}</Text>
        <View style={styles.onboardList}>
          <Text style={styles.onboardListItem}>{body}</Text>
        </View>
      </View>
    );
  }
}
const TopView = injectIntl(_TopView);

class _TutorialScreen extends React.Component {
  render() {
    var pages = PAGES.map((val, i) => this._renderPage(i));
    return <Carousel
      indicatorOffset={0}
      indicatorColor="#FFFFFF"
      indicatorSize={25}
      indicatorSpace={15}
      animate={false}
      loop={false}
      >
      {pages}
    </Carousel>;
  }

  _renderPage(pageId: number) {
    var contents = this._renderPageContents(pageId);
    var windowSize = Dimensions.get('window');
    return <View
      style={{
        flex: 1,
        width: windowSize.width,
        height: windowSize.height,
        backgroundColor: 'black',
      }}
      key={pageId}>
    {contents}
    </View>;
  }

  _renderPageContents(pageID: number) {
    // We manually insert a bottomFade into each page below,
    // so that we can stick buttons/links/text on top of the fade.

    var bottomFade = <LinearGradient
      start={[0.0, 0.0]} end={[0.0, 1.0]}
      locations={[0.0, 0.8, 1.0]}
      colors={['#00000000', '#000000CC', '#000000CC']}
      style={styles.bottomFade} />;

    if (pageID === 0) {
      return <LaunchScreen>{bottomFade}</LaunchScreen>;
    } else if (pageID === 1) {
      return <Image
        style={styles.container}
        source={require('./images/Onboard1.jpg')}>
        {bottomFade}
        <Image
        style={[styles.container, styles.centerItems]}
          source={require('./images/Onboard1Text.png')}>
          <TopView page={0} />
        </Image>
      </Image>;
    } else if (pageID === 2) {
      return <Image
        style={[styles.container, styles.centerItems]}
        source={require('./images/Onboard2.jpg')}>
        {bottomFade}
        <TopView page={1} />
      </Image>;
    } else if (pageID === 3) {
      return <View style={styles.container}>
        <Image
          style={styles.container}
          source={require('./images/Onboard3.jpg')}>
          {bottomFade}
          <Image
            style={[styles.container, styles.centerItems, styles.topAndBottom]}
            source={require('./images/Onboard3Text.png')}>
            <TopView page={2} />
            <LoginButtonWithAlternate
              onLogin={this.props.onLogin}
              onNoLogin={this.props.onNoLogin}
              noLoginText={this.props.intl.formatMessage(messages.nologin)}
              />
          </Image>
        </Image>
      </View>;
    }
  }
}
export default injectIntl(_TutorialScreen);

const styles = StyleSheet.create({
  topAndBottom: {
    justifyContent: 'space-between',
  },
  onboardHeader: {
    color: 'white',
    fontSize: normalize(30),
    lineHeight: normalize(40),
    fontWeight: 'bold',
    marginTop: normalize(20),
    height: normalize(60),
  },
  onboardList: {
  },
  onboardListItem: {
    color: 'white',
    lineHeight: normalize(35),
    fontSize: normalize(20),
    fontWeight: 'bold',
  },
  centerItems: {
    alignItems: 'center',
    justifyContent: 'flex-start',
  },
  bottomFade: {
    position: 'absolute',
    flex: 1,
    height: 100,
    bottom: 0,
    left: 0,
    right: 0,
  },
  container: {
    flex: 1,
    backgroundColor: 'transparent',
    // Image's source contains explicit size, but we want
    // it to prefer flex: 1
    width: undefined,
    height: undefined,
  },
});
