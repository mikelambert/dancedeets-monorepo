/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  AlertIOS,
  Image,
  Platform,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  View,
} from 'react-native';
import { connect } from 'react-redux';
import { logOutWithPrompt } from '../actions';
import { linkColor } from '../Colors';
import {
  Button,
  Card,
  Heading1,
  HorizontalView,
  normalize,
  Text,
} from '../ui';
import { purpleColors } from '../Colors';
import { track } from '../store/track';
import type { Dispatch } from '../actions/types';
import { ShareDialog, MessageDialog } from 'react-native-fbsdk';
import Share from 'react-native-share';
import {
  injectIntl,
  intlShape,
  defineMessages,
} from 'react-intl';
import NativeEnv from 'react-native-native-env';

const Mailer = require('NativeModules').RNMail;

const STATUSBAR_HEIGHT = Platform.OS === 'ios' ? 20 : 0;

const messages = defineMessages({
  credits: {
    id: 'credits.title',
    defaultMessage: 'Dancedeets Credits',
    description: 'Header of our Credits section',
  },
  tagline: {
    id: 'dancedeets.tagline',
    defaultMessage: 'Street Dance Events. Worldwide.',
    description: 'Our tagline for DanceDeets, used when sharing the app/site'
  },
  shareTitle: {
    id: 'share.title',
    defaultMessage: 'Share DanceDeets',
    description: 'Title for our card with all the share buttons, to share the app',
  },
  shareFacebook: {
    id: 'share.facebook',
    defaultMessage: 'Share on FB',
    description: 'Share this on Facebook wall',
  },
  shareFacebookMessenger: {
    id: 'share.facebookMessenger',
    defaultMessage: 'Send FB Message',
    description: 'Share this through Facebook message',
  },
  shareGeneric: {
    id: 'share.generic',
    defaultMessage: 'Send Message',
    description: 'Share this using the native mobile share experience',
  },
  friendsUsing: {
    id: 'profile.friendsUsing',
    defaultMessage: '{count} friends using DanceDeets',
    description: 'A count of how many of the user\'s friends are using the app',
  },
  logout: {
    id: 'login.logout',
    defaultMessage: 'Logout',
    description: 'Button to log out of the app',
  },
  buttonNotificationSettings: {
    id: 'buttons.notificationSettings',
    defaultMessage: 'Notification Settings(TODO)',
    description: 'Configure the app notification preferences',
  },
  buttonSendFeedback: {
    id: 'buttons.sendFeedback',
    defaultMessage: 'Send Feedback',
    description: 'Button to send feedback to DanceDeets about the app/site',
  },
  buttonAdvertisePromote: {
    id: 'buttons.advertisePromote',
    defaultMessage: 'Advertise/Promote',
    description: 'Button to contact DanceDeets about advertising/promoting events in the app',
  },
  profileDetailsHeader: {
    id: 'profile.detailsHeader',
    defaultMessage: 'Dance Events:',
    description: 'Header for details about the user',
  },
  profileDetailsContents: {
    id: 'profile.detailsContents',
    defaultMessage: '– Added: {handAdded, number}\n– Auto-contributed: {autoAdded, number}',
    description: 'Details about the user',
  },
});

const credits = [
  [
    'Web & App Programming',
    ['Mike Lambert'],
  ],
  [
    'Logo',
    ['James "Cricket" Colter'],
  ],
  [
    'App Login Photos',
    ['dancephotos.ch'],
  ],
  [
    'Translations',
    [
      'French: Mai Le',
      'Japanese: Huu Rock',
      'Chinese: Wei and King Kong',
    ]
  ]
];

class CreditSubList extends React.Component {
  render() {
    const subcreditGroups = this.props.list.map((x) => <Text key={x} style={{left: 10}}>- {x}</Text>);
    return <View>{subcreditGroups}</View>;
  }
}

class _Credits extends React.Component {
  render() {
    const creditHeader = <Heading1 style={{marginBottom: 5}}>{this.props.intl.formatMessage(messages.credits)}</Heading1>;
    const creditGroups = credits.map((x) => <View key={x[0]} ><Text style={{fontWeight: 'bold'}}>{x[0]}:</Text><CreditSubList list={x[1]}/></View>);
    const version = <Text style={styles.versionStyle}>Version: {NativeEnv.get('VERSION_NAME')}</Text>;
    return <Card style={this.props.style}>
      {creditHeader}
      {version}
      {creditGroups}
    </Card>;
  }
}
const Credits = injectIntl(_Credits);

const shareLinkContent = {
  contentType: 'link',
  contentUrl: 'http://www.dancedeets.com',
  contentDescription: '',
};

class _ShareButtons extends React.Component {
  getShareLinkContent() {
    return Object.assign({}, shareLinkContent, {contentDescription: this.props.intl.formatMessage(messages.tagline)});
  }

  render() {
    return (
      <Card>
        <Heading1>{this.props.intl.formatMessage(messages.shareTitle)}</Heading1>

        <Button
          size="small"
          caption={this.props.intl.formatMessage(messages.shareFacebook)}
          icon={require('../login/icons/facebook.png')}
          onPress={() => {
            track('Share DanceDeets', {Button: 'Share FB Post'});
            ShareDialog.show(this.getShareLinkContent());
          }}
          style={styles.noFlexButton}
        />
        <Button
          size="small"
          caption={this.props.intl.formatMessage(messages.shareFacebookMessenger)}
          icon={require('../login/icons/facebook-messenger.png')}
          onPress={() => {
            track('Share DanceDeets', {Button: 'Send FB Message'});
            MessageDialog.show(this.getShareLinkContent());
          }}
          style={styles.noFlexButton}
        />
        <Button
          size="small"
          caption={this.props.intl.formatMessage(messages.shareGeneric)}
          icon={Platform.OS === 'ios' ? require('./share-icons/small-share-ios.png') : require('./share-icons/small-share-android.png')}
          onPress={() => {
            track('Share DanceDeets', {Button: 'Send Native'});
            const localizedShareLinkContent = this.getShareLinkContent();
            Share.open({
              share_text: localizedShareLinkContent.contentDescription,
              share_URL: localizedShareLinkContent.contentUrl,
              title: 'DanceDeets',
            }, (e) => {
              console.warn(e);
            });
          }}
          style={styles.noFlexButton}
        />
      </Card>
    );
  }
}
const ShareButtons = injectIntl(_ShareButtons);

function sendEmail() {
  track('Send Feedback');
  Mailer.mail({
      subject: 'DanceDeets Feeback',
      recipients: [`feedback+${Platform.OS}@dancedeets.com`],
      body: '',
    }, (error, event) => {
        if (error) {
          AlertIOS.alert('Error', 'Please email us at feedback@dancedeets.com');
        }
    });
}

function sendAdvertisingEmail() {
  track('Advertising');
  Mailer.mail({
      subject: 'Advertising/Promotion Interest',
      recipients: ['advertising@dancedeets.com'],
      body: '',
    }, (error, event) => {
        if (error) {
          AlertIOS.alert('Error', 'Please email us at feedback@dancedeets.com');
        }
    });
}

class _UserProfile extends React.Component {
  render() {
    const logoutButton = <Button
      size="small"
      caption={this.props.intl.formatMessage(messages.logout)}
      onPress={() => this.props.logOutWithPrompt(this.props.intl)}
    />;
    const user = this.props.user;
    if (!user) {
      // Don't render anything if we don't yet have a user
      return logoutButton;
    }
    const friendCount = user.friends.data.length || 0;
    const image = user.picture ? <Image style={styles.profileImageSize} source={{uri: user.picture.data.url}}/> : null;
    let friendsCopy = null;
    if (friendCount !== 0) {
      friendsCopy = <Text style={{marginBottom: 10}}>{this.props.intl.formatMessage(messages.friendsUsing, {count: friendCount})}</Text>;
    }

    return <Card>
      <HorizontalView>
        <View style={styles.profileLeft}>
          <View style={[styles.profileImageSize, styles.profileImage]}>{image}</View>
        </View>
        <View style={styles.profileRight}>
          <Heading1>{user.profile.name || ' '}</Heading1>
          <Text style={{fontStyle: 'italic', marginBottom: 10}}>{user.ddUser.formattedCity || ' '}</Text>
          {logoutButton}
        </View>
      </HorizontalView>
      <View>
        {friendsCopy}
        <Text style={{fontWeight: 'bold'}}>{this.props.intl.formatMessage(messages.profileDetailsHeader)}</Text>
        <Text>{this.props.intl.formatMessage(messages.profileDetailsContents, {
          handAdded: user.ddUser.num_hand_added_events || 0,
          autoAdded: user.ddUser.num_auto_added_events || 0,
        })}</Text>
      </View>
    </Card>;
  }
}
const UserProfile = connect(
  state => ({
    user: state.user.userData,
  }),
  (dispatch: Dispatch) => ({
    logOutWithPrompt: (intl) => dispatch(logOutWithPrompt(intl)),
  }),
)(injectIntl(_UserProfile));


class _Profile extends React.Component {

  render() {
    return <ScrollView style={styles.container} contentContainerStyle={styles.containerContent}>

      <UserProfile />

      <ShareButtons />

      {Platform.OS === 'android' ? <Button size="small" caption={this.props.intl.formatMessage(messages.buttonNotificationSettings)}/> : null}

      <Button size="small" caption={this.props.intl.formatMessage(messages.buttonSendFeedback)} onPress={sendEmail} style={styles.noFlexButton}/>

      <Button size="small" caption={this.props.intl.formatMessage(messages.buttonAdvertisePromote)} onPress={sendAdvertisingEmail} style={styles.noFlexButton}/>

      <Credits />

    </ScrollView>;
  }
}
export default injectIntl(_Profile);

const styles = StyleSheet.create({
  noFlexButton: {
    flex: 0,
    marginTop: normalize(10),
  },
  container: {
    flex: 1,
    backgroundColor: 'black',
  },
  containerContent: {
    top: STATUSBAR_HEIGHT,
    backgroundColor: 'black',
    alignItems: 'center',
    justifyContent: 'space-around',
  },
  profileName: {
    fontSize: 22,
  },
  profileLeft: {
    marginRight: 10,
  },
  profileRight: {
  },
  profileImageSize: {
    width: 90,
    height: 90,
    borderRadius: 5,
  },
  profileImage: {
    marginBottom: 10,
    borderWidth: 1,
    borderColor: purpleColors[0],
  },
  bottomSpacedContent: {
    flex: 1,
    marginTop: 20,
    justifyContent: 'space-around',
  },
  link: {
    color: linkColor,
  },
  versionStyle: {
    fontStyle: 'italic',
  },
});
