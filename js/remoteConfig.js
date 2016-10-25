/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { RemoteConfig } from 'react-native-firebase3';

async function loadConfig() {
  if (__DEV__) {
    RemoteConfig.setDeveloperMode(true);
  }
  await RemoteConfig.fetchWithExpirationDuration(30 * 15);
  await RemoteConfig.activateFetched();
}

loadConfig();

export async function get(value: string) {
  return JSON.parse(await RemoteConfig.getString(value));
}
