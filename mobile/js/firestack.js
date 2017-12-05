/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import firebase from 'react-native-firebase';
import { connect } from 'react-redux';
import type { Dispatch } from './actions/types';
import { setFirebaseState } from './actions';

// TODO: How do we turn on database persistence? So it saves locally without network?

class _TrackFirebase extends React.Component<{
  path: string,
  children: React.Node,
  // If set, render passing in the state, instead of just rendering children
  renderContents?: (contents: any) => React.Element<*>,

  // Self-managed props
  setFirebaseState: (key: string, value: any) => void,
  firebaseData: Object,
}> {
  _setHandler: boolean;

  constructor(props: any) {
    super(props);
    (this: any).handleValueChange = this.handleValueChange.bind(this);
    this._setHandler = false;
  }

  componentWillMount() {
    const dbRef = firebase.database().ref(this.props.path);
    console.log(`Installing handler on path: ${this.props.path}`);
    dbRef.on('value', this.handleValueChange);
    this._setHandler = true;
  }

  componentWillUnmount() {
    if (this._setHandler) {
      console.log(`Uninstalling handler on path: ${this.props.path}`);
      firebase
        .database()
        .ref(this.props.path)
        .off('value', this.handleValueChange);
    }
  }

  handleValueChange(snapshot) {
    if (snapshot.val()) {
      this.props.setFirebaseState(this.props.path, snapshot.val());
    }
  }

  render() {
    if (this.props.renderContents) {
      return this.props.renderContents(
        this.props.firebaseData[this.props.path]
      );
    } else {
      return this.props.children;
    }
  }
}
export const TrackFirebase = connect(
  state => ({
    firebaseData: state.firebase,
  }),
  (dispatch: Dispatch) => ({
    setFirebaseState: (key, value) => dispatch(setFirebaseState(key, value)),
  })
)(_TrackFirebase);

