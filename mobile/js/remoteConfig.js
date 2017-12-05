/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import firebase from 'react-native-firebase';

async function loadConfig() {
  if (__DEV__) {
    firebase.config().enableDeveloperMode();
  }
  await firebase.config().fetch();
  await firebase.config().activateFetched();
}

loadConfig();

export async function get(value: String): any {
  const result = await firebase.config().getValue(value);
  if (result) {
    return JSON.parse(result.val());
  }
  return null;
}
