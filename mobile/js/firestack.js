/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import Firestack from 'react-native-firestack';
import { connect } from 'react-redux';
import type { Dispatch } from './actions/types';
import { setFirebaseState } from './actions';

const configurationOptions = {
  debug: true,
};
const firestack = new Firestack(configurationOptions);
firestack.on('debug', msg => console.log('Received debug message', msg));
firestack.database.setPersistence(true);

class _TrackFirebase extends React.Component {
  constructor(props: any) {
    super(props);
    (this: any).handleValueChange = this.handleValueChange.bind(this);
  }

  handleValueChange(snapshot) {
    if (snapshot.val()) {
      this.props.setFirebaseState(this.props.storageKey, snapshot.val());
    }
  }

  componentWillMount() {
    firestack.database.ref(this.props.path).on('value', this.handleValueChange);
  }

  componentWillUnmount() {
    firestack.database.ref(this.props.path).off('value', this.handleValueChange);
  }

  render() {
    return this.props.children;
  }
}
export const TrackFirebase = connect(
  state => ({
  }),
  (dispatch: Dispatch, props) => ({
    setFirebaseState: (key, value) => dispatch(setFirebaseState(key, value)),
  }),
)(_TrackFirebase);

export default firestack;
