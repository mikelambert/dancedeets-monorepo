/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Image,
  StyleSheet,
  View,
} from 'react-native';
import { connect } from 'react-redux';
import { logOutWithPrompt } from '../actions';
import { performRequest } from '../api/fb';
import {
  Button,
  Text,
} from '../ui';
import type { Dispatch } from '../actions/types';

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
    const creditHeader = <Text style={{fontWeight: 'bold', fontSize: 20}}>Dancedeets Credits</Text>
    const creditGroups = credits.map((x) => <View key={x[0]} ><Text style={{fontWeight: 'bold'}}>{x[0]}:</Text><CreditSubList list={x[1]}/></View>);
    return <View style={this.props.style}>{creditHeader}{creditGroups}</View>;
  }
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
      {image}
      <Text>{this.state.name}</Text>
      <Text>show current city?</Text>

      {this.state.friendCount ? <Text>{this.state.friendCount} friends using DanceDeets</Text> : null}
      <Button size="small" caption="Invite more friends"/>

      <Button
        size="small"
        icon={require('../login/icons/facebook.png')}
        caption="Logout"
        onPress={this.props.logOutWithPrompt}
        />
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
      <ProfileComponent style={{height:300}}/>
      <Button size="small" caption="Send Feedback" />

      <Credits style={{marginTop: 20}}/>
    </View>;
  }
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
    alignItems: 'center'
  },
  profileImage: {
    width: 150,
    height: 150,
  }
});
