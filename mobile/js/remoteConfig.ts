/**
 * Copyright 2016 DanceDeets.
 */

import firebase from 'react-native-firebase';

async function loadConfig(): Promise<void> {
  if (__DEV__) {
    firebase.config().enableDeveloperMode();
  }
  await firebase.config().fetch();
  await firebase.config().activateFetched();
}

loadConfig();

export async function get<T>(value: string): Promise<T | null> {
  const result = await firebase.config().getValue(value);
  if (result) {
    return JSON.parse(result.val()) as T;
  }
  return null;
}
