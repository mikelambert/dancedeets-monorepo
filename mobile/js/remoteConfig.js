/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import firebase from './firebase';

async function loadConfig() {
  if (__DEV__) {
    firebase.config().setDeveloperMode(true);
  }
  await firebase.config().fetch(60 * 10); // 10 minutes
  await firebase.config().activateFetched();
}

loadConfig();

export async function get(value: string): any {
  const snapshot = await firebase.config().getValue(value);
  if (snapshot && snapshot.val()) {
    return JSON.parse(snapshot.val());
  }
  return null;
}
