/**
 * Copyright 2016 DanceDeets.
 *
 * Firebase Realtime Database - modular API
 */

import * as React from 'react';
import database, { FirebaseDatabaseTypes } from '@react-native-firebase/database';
import { connect } from 'react-redux';
import type { Dispatch } from './actions/types';
import { setFirebaseState } from './actions';

// TODO: How do we turn on database persistence? So it saves locally without network?

interface TrackFirebaseOwnProps {
  path: string;
  children: React.ReactNode;
  // If set, render passing in the state, instead of just rendering children
  renderContents?: (contents: unknown) => React.ReactElement;
}

interface TrackFirebaseStateProps {
  firebaseData: Record<string, unknown>;
}

interface TrackFirebaseDispatchProps {
  setFirebaseState: (key: string, value: unknown) => void;
}

type TrackFirebaseProps = TrackFirebaseOwnProps & TrackFirebaseStateProps & TrackFirebaseDispatchProps;

class _TrackFirebase extends React.Component<TrackFirebaseProps> {
  _setHandler: boolean;

  constructor(props: TrackFirebaseProps) {
    super(props);
    this.handleValueChange = this.handleValueChange.bind(this);
    this._setHandler = false;
  }

  componentDidMount(): void {
    const dbRef = database().ref(this.props.path);
    console.log(`Installing handler on path: ${this.props.path}`);
    dbRef.on('value', this.handleValueChange);
    this._setHandler = true;
  }

  componentWillUnmount(): void {
    if (this._setHandler) {
      console.log(`Uninstalling handler on path: ${this.props.path}`);
      database()
        .ref(this.props.path)
        .off('value', this.handleValueChange);
    }
  }

  handleValueChange(snapshot: FirebaseDatabaseTypes.DataSnapshot): void {
    if (snapshot.val()) {
      this.props.setFirebaseState(this.props.path, snapshot.val());
    }
  }

  render(): React.ReactNode {
    if (this.props.renderContents) {
      return this.props.renderContents(
        this.props.firebaseData[this.props.path]
      );
    } else {
      return this.props.children;
    }
  }
}

interface RootState {
  firebase: Record<string, unknown>;
}

export const TrackFirebase = connect<TrackFirebaseStateProps, TrackFirebaseDispatchProps, TrackFirebaseOwnProps, RootState>(
  (state: RootState) => ({
    firebaseData: state.firebase,
  }),
  (dispatch: Dispatch) => ({
    setFirebaseState: (key: string, value: unknown) => dispatch(setFirebaseState(key, value)),
  })
)(_TrackFirebase);
