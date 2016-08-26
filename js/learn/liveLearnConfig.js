/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {
  defaultTutorials,
  defaultBlogs,
} from './learnConfig';
import { RemoteConfig } from 'react-native-firebase3';

async function loadConfig() {
  RemoteConfig.setNamespacedDefaults({
    tutorials: JSON.stringify(defaultTutorials),
    blogs: JSON.stringify(defaultBlogs),
  }, 'Learn');
  await RemoteConfig.fetchWithExpirationDuration(30 * 15);
  await RemoteConfig.activateFetched();
}

loadConfig();

export async function getRemoteBlogs() {
  return JSON.parse(await RemoteConfig.getNamedspacedString('blogs', 'Learn'));
}
export async function getRemoteTutorials() {
  return JSON.parse(await RemoteConfig.getNamedspacedString('tutorials', 'Learn'));
}
