/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { RemoteConfig } from 'react-native-firebase3';
import {
  defaultTutorials,
  defaultBlogs,
} from './learnConfig';

async function loadConfig() {
  if (__DEV__) {
    RemoteConfig.setDeveloperMode(true);
  }
  RemoteConfig.setNamespacedDefaults({
    blogs: JSON.stringify(defaultBlogs),
  }, 'Learn');
  await RemoteConfig.fetchWithExpirationDuration(30 * 15);
  await RemoteConfig.activateFetched();
}

// loadConfig();

export async function getRemoteBlogs() {
  return JSON.parse(await RemoteConfig.getNamespacedString('blogs', 'Learn'));
}
export function getRemoteTutorials() {
  return defaultTutorials;
}
