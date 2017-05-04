/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { RemoteConfig } from 'react-native-firebase3';

async function loadConfig() {
  if (__DEV__) {
    RemoteConfig.setDeveloperMode(true);
  }
  await RemoteConfig.fetchWithExpirationDuration(60 * 10);
  await RemoteConfig.activateFetched();
}

// loadConfig();

export async function getRemoteBlogs() {
  return JSON.parse(await RemoteConfig.getNamespacedString('blogs', 'Learn'));
}
