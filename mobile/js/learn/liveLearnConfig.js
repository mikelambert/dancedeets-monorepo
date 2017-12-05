/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import firebase from 'react-native-firebase';

// eslint-disable-next-line no-unused-vars
async function loadConfig() {
  if (__DEV__) {
    firebase.config().enableDeveloperMode();
  }
  await firebase.config().fetch();
  await firebase.config().activateFetched();
}

// loadConfig();

export async function getRemoteBlogs() {
  const result = await firebase.config().getValue('Learn:blogs');
  if (result) {
    return JSON.parse(result.val());
  }
}
