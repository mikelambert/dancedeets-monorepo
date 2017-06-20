/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import RNFirebase from 'react-native-firebase';
import Snapshot from 'react-native-firebase/lib/modules/database/snapshot';
import { connect } from 'react-redux';
import type { Dispatch } from './actions/types';

const configurationOptions = {
  debug: true,
  persistence: true,
};
const firebase = RNFirebase.initializeApp(configurationOptions);

export class TrackFirebase extends React.Component {
  props: {
    path: string,
    children?: React.Element<*>,
    // If set, render passing in the state, instead of just rendering children
    renderContents?: (contents: any) => React.Element<*>,
  };

  state: {
    firebase: any,
  };

  _dbRef: Object;

  constructor(props: any) {
    super(props);
    (this: any).handleValueChange = this.handleValueChange.bind(this);
  }

  componentWillMount() {
    this._dbRef = firebase.database().ref(this.props.path);
    this._dbRef.on('value', this.handleValueChange);
    console.log(`Installing handler on path: ${this.props.path}`);
  }

  componentWillUnmount() {
    console.log(`Uninstalling handler on path: ${this.props.path}`);
    this._dbRef.off('value', this.handleValueChange);
  }

  handleValueChange(snapshot: Snapshot) {
    if (snapshot.val()) {
      this.setState({ firebase: snapshot.val() });
    }
  }

  render() {
    if (this.props.renderContents) {
      return this.props.renderContents(this.state.firebase);
    } else {
      return this.props.children;
    }
  }
}

export default firebase;
