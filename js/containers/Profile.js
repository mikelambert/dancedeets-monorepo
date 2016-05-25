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

import { navigatePush, navigatePop } from '../actions';
import { performRequest } from '../api/fb';
import {
  Button,
  Text,
} from '../ui';
import type { Dispatch } from '../actions/types';

const credits = [
  [
    'Website, App, Programming',
    ['DanceDeets'],
  ],
  [
    'Logo',
    ['Cricket'],
  ],
  [
    'Mobile App Photos',
    ['dancephotos.ch'],
  ],
  [
    'Japan Events',
    [
      'Enter The Stage',
      'Dance Delight',
      'DEWS',
      'Tokyo Dance Life',
    ],
  ],
  [
    'Korea Events',
    ['Street Dance Korea'],
  ],
];

class CreditSubList extends React.Component {
  render() {
    const subcreditGroups = this.props.list.map((x) => <Text style={{left: 10}}>- {x}</Text>);
    return <View>{subcreditGroups}</View>;
  }
}

class Credits extends React.Component {
  render() {
    const creditHeader = <Text style={{fontWeight: 'bold', fontSize: 20}}>Credits</Text>
    const creditGroups = credits.map((x) => <View><Text style={{fontWeight: 'bold'}}>{x[0]}:</Text><CreditSubList list={x[1]}/></View>);
    return <View style={this.props.style}>{creditHeader}{creditGroups}</View>;
  }
}

class Profile extends React.Component {
  props: {
  };

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
    const profileData = await performRequest('GET', 'me?fields=name');
    this.setState({...this.state, name: profileData.name});
  }

  async setupProfilePhoto() {
    const pictureData = await performRequest('GET', 'me/picture?type=large&fields=url&redirect=0');
    this.setState({...this.state, url: pictureData.data.url});
  }

  async setupProfileFriends() {
    const friendData = await performRequest('GET', 'me/friends?limit=1000&fields=id');
    this.setState({...this.state, friendCount: friendData.data.length});
  }

  componentWillMount() {
    this.setupProfilePhoto();
    this.setupProfileName();
    this.setupProfileFriends();
  }

  render() {
    const image = this.state.url ? <Image style={styles.profileImage} source={{uri: this.state.url}}/> : null;
    console.log(image);
    return <View style={styles.container}>
      {image}
      <Text>{this.state.name}</Text>
      <Text>show current city?</Text>

      {this.state.friendCount?<Text>{this.state.friendCount} friends using DanceDeets</Text>:null}
      <Button caption="Invite more friends"/>

      <Button
        icon={require('../login/icons/facebook.png')}
        caption="Logout"
        />

      <Button caption="Send Feedback" />

      <Credits style={{marginTop: 20}}/>
    </View>;
  }
}

export default connect(
  state => ({
    navigationState: state.navigationState
  }),
  (dispatch: Dispatch) => ({
    onNavigate: (destState) => dispatch(navigatePush(destState)),
    onBack: () => dispatch(navigatePop())
  }),
)(Profile);


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
