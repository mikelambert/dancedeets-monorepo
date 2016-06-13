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
  Heading1,
  HorizontalView,
  Text,
} from '../ui';
import { purpleColors } from '../Colors';
import { track } from '../store/track';
import type { Dispatch } from '../actions/types';
import { ShareDialog, MessageDialog } from 'react-native-fbsdk';
import Share from 'react-native-share';

const Mailer = require('NativeModules').RNMail;

const STATUSBAR_HEIGHT = Platform.OS === 'ios' ? 20 : 0;


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
];

class CreditSubList extends React.Component {
  render() {
    const subcreditGroups = this.props.list.map((x) => <Text key={x} style={{left: 10}}>- {x}</Text>);
    return <View>{subcreditGroups}</View>;
  }
}

class Credits extends React.Component {
  render() {
    const creditHeader = <Heading1>Dancedeets Credits</Heading1>;
    const creditGroups = credits.map((x) => <View key={x[0]} ><Text style={{fontWeight: 'bold'}}>{x[0]}:</Text><CreditSubList list={x[1]}/></View>);
    return <View style={this.props.style}>{creditHeader}{creditGroups}</View>;
  }
}

const shareLinkContent = {
  contentType: 'link',
  contentUrl: 'http://www.dancedeets.com',
  contentDescription: 'Street Dance Events, Worldwide!',
};

class ShareButtons extends React.Component {
  render() {
    return (
      <View>
        <Heading1>Share DanceDeets</Heading1>

        <Button
          size="small"
          caption="Share on FB"
          icon={require('../login/icons/facebook.png')}
          onPress={() => {
            track('Share DanceDeets', {Button: 'Share FB Post'});
            ShareDialog.show(shareLinkContent);
          }}
          style={styles.noFlexButton}
        />
        <Button
          size="small"
          caption="Send FB Message"
          icon={require('../login/icons/facebook-messenger.png')}
          onPress={() => {
            track('Share DanceDeets', {Button: 'Send FB Message'});
            MessageDialog.show(shareLinkContent);
          }}
          style={styles.noFlexButton}
        />
        <Button
          size="small"
          caption="Send Message"
          icon={Platform.OS === 'ios' ? require('./share-icons/small-share-ios.png') : require('./share-icons/small-share-android.png')}
          onPress={() => {
            track('Share DanceDeets', {Button: 'Send Native'});
            Share.open({
              share_text: shareLinkContent.contentDescription,
              share_URL: shareLinkContent.contentUrl,
              title: 'DanceDeets',
            }, (e) => {
              console.warn(e);
            });
          }}
          style={styles.noFlexButton}
        />
      </View>
    );
  }
}

function sendEmail() {
  track('Send Feedback');
  Mailer.mail({
      subject: 'DanceDeets Feeback',
      recipients: ['feedback@dancedeets.com'],
      body: '',
    }, (error, event) => {
        if (error) {
          AlertIOS.alert('Error', 'Please email us at feedback@dancedeets.com');
        }
    });
}

class _UserProfile extends React.Component {
  render() {
    const user = this.props.user;
    const image = user.picture ? <Image style={styles.profileImageSize} source={{uri: user.picture.data.url}}/> : null;
    let friendsCopy = <Text style={{marginBottom: 10}}>{user.friends.data.length || 0} friends using DanceDeets</Text>;
    if (user.friends.data.length === 0) {
      friendsCopy = null;
    }

    return <HorizontalView>
        <View>
          <View style={[styles.profileImageSize, styles.profileImage]}>{image}</View>
          <TouchableOpacity onPress={this.props.logOutWithPrompt}>
            <Text style={styles.link}>Logout</Text>
          </TouchableOpacity>
        </View>
        <View>
          <Heading1>{user.profile.name || ' '}</Heading1>
          <Text style={{fontStyle: 'italic', marginBottom: 10}}>{user.ddUser.location || ' '}</Text>
          {friendsCopy}
          <Text style={{fontWeight: 'bold'}}>Dance Events:</Text>
          <Text>– Added: {user.ddUser.num_hand_added_events || 0}</Text>
          <Text>– Auto-contributed: {user.ddUser.num_auto_added_events || 0}</Text>
        </View>
      </HorizontalView>;
  }
}
const UserProfile = connect(
  state => ({
    user: state.user.userData,
  }),
  (dispatch: Dispatch) => ({
    logOutWithPrompt: () => dispatch(logOutWithPrompt()),
  }),
)(_UserProfile);

class Card extends React.Component {
  render() {
    return <View style={styles.card}>
    {this.props.children}
    </View>
  }
}

export default class Profile extends React.Component {
  render() {
    return <ScrollView style={styles.container} contentContainerStyle={styles.containerContent}>
      <Card>
        <UserProfile />
      </Card>

      <Card>
        <ShareButtons />
      </Card>

      <Button size="small" caption="Notification Settings"/>

      <Button size="small" caption="Send Feedback" onPress={sendEmail} style={{marginTop: 5}}/>

      <Card>
        <Credits />
      </Card>

    </ScrollView>;
  }
}

const styles = StyleSheet.create({
  noFlexButton: {
    flex: 0,
    marginTop: 5,
  },
  container: {
    flex: 1,
    backgroundColor: 'black',
  },
  containerContent: {
    top: STATUSBAR_HEIGHT,
    flex: 1,
    backgroundColor: 'black',
    alignItems: 'center',
    justifyContent: 'space-around',
  },
  profileName: {
    fontSize: 22,
  },
  card: {
    backgroundColor: purpleColors[3],
    borderColor: purpleColors[0],
    borderWidth: 1,
    borderRadius: 10,
    padding: 10,
    margin: 10,
    // So it looks okay one wide screen devices
    width: 350,
  },
  profileImageSize: {
    width: 100,
    height: 100,
    borderRadius: 5,
  },
  profileImage: {
    marginRight: 10,
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
});
