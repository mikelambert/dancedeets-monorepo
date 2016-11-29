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
  const result = await RemoteConfig.getString(value);
  if (result) {
    return JSON.parse(result);
  } else {
    return null;
  }
}
