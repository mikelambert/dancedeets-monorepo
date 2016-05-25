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
import { Text } from '../ui';
import type { Dispatch } from '../actions/types';

class Profile extends React.Component {
  props: {
  };

  state: {
    name: ?string,
    url: ?string,
  };

  constructor(props) {
    super(props);
    this.state = {
      name: null,
      url: null,
    };
  }

  async setupProfileName() {
    const profileData = await performRequest('GET', 'me?fields=name');
    this.setState({...this.state, name: profileData.name});
  }

  async setupProfilePhoto() {
    const profileData = await performRequest('GET', 'me?fields=picture');
    const pictureData = profileData.picture.data;
    this.setState({...this.state, url: pictureData.url});
  }

  componentWillMount() {
    this.setupProfilePhoto();
    this.setupProfileName();
  }

  render() {
    const image = this.state.url ? <Image style={styles.profileImage} source={{uri: this.state.url}}/> : null;
    console.log(image);
    return <View style={styles.container}>
      {image}
      <Text>{this.state.name}</Text>
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
    width: 100,
    height: 100,
  }
});
