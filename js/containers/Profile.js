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
  StyleSheet,
  TouchableOpacity,
  View,
} from 'react-native';
import { connect } from 'react-redux';
import { logOutWithPrompt } from '../actions';
import { performRequest } from '../api/fb';
import { linkColor } from '../Colors';
import {
  Button,
  HorizontalView,
  Text,
} from '../ui';
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
    const creditHeader = <Text style={{fontWeight: 'bold', fontSize: 20}}>Dancedeets Credits</Text>;
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
        <Text>Share DanceDeets:</Text>

        <Button caption="Share on FB"
          onPress={() => {
            track('Share DanceDeets', {Button: 'Share FB Post'});
            ShareDialog.show(shareLinkContent);
          }}
        />
        <Button caption="Send FB Message"
          onPress={() => {
            track('Share DanceDeets', {Button: 'Send FB Message'});
            MessageDialog.show(shareLinkContent);
          }}
        />
        <Button caption="Send Message"
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

class _ProfileComponent extends React.Component {
  state: {
    name: ?string,
    url: ?string,
    friendCount: ?number,
  };

  constructor(props) {
    super(props);
    this.state = {
      name: null,
      url: null,
      friendCount: null,
    };
  }

  async setupProfileName() {
    const profileData = await performRequest('GET', 'me', {fields: 'name'});
    this.setState({...this.state, name: profileData.name});
  }

  async setupProfilePhoto() {
    const pictureData = await performRequest('GET', 'me/picture', {type: 'large', fields: 'url', redirect: '0'});
    this.setState({...this.state, url: pictureData.data.url});
  }

  async setupProfileFriends() {
    const friendData = await performRequest('GET', 'me/friends', {limit: '1000', fields: 'id'});
    this.setState({...this.state, friendCount: friendData.data.length});
  }

  componentWillMount() {
    this.setupProfilePhoto();
    this.setupProfileName();
    this.setupProfileFriends();
  }

  render() {
    const image = this.state.url ? <Image style={styles.profileImage} source={{uri: this.state.url}}/> : null;
    return <View style={this.props.style}>
      <HorizontalView>
        {image}
        <View>
          <Text style={styles.profileName}>{this.state.name}</Text>
          {this.state.friendCount ? <Text>{this.state.friendCount} friends using DanceDeets</Text> : null}
          <TouchableOpacity onPress={this.props.logOutWithPrompt}>
            <Text style={styles.link}>Logout</Text>
          </TouchableOpacity>
        </View>
      </HorizontalView>

      <ShareButtons />

      <HorizontalView style={{marginTop: 10}}>
      <Button size="small" caption="Notification Settings"/>
      </HorizontalView>

    </View>;
  }
}
const ProfileComponent = connect(
  state => ({
  }),
  (dispatch: Dispatch) => ({
    logOutWithPrompt: () => dispatch(logOutWithPrompt()),
  }),
)(_ProfileComponent);

export default class Profile extends React.Component {
  render() {
    return <View style={styles.container}>
      <ProfileComponent style={styles.profileComponent}/>
      <Button size="small" caption="Send Feedback" onPress={sendEmail}/>

      <Credits style={{marginTop: 20}}/>
    </View>;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
    alignItems: 'center',
  },
  profileName: {
    fontSize: 22,
  },
  profileComponent: {
    top: STATUSBAR_HEIGHT,
    height: 300,
  },
  profileImage: {
    marginRight: 10,
    width: 100,
    height: 100,
  },
  link: {
    color: linkColor,
  },
});
