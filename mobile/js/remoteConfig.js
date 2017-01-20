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
  await RemoteConfig.fetchWithExpirationDuration(60 * 10); // 10 minutes
  await RemoteConfig.activateFetched();
}

loadConfig();

export async function get(value: string): any {
  const result = await RemoteConfig.getString(value);
  if (result) {
    return JSON.parse(result);
  }
  return null;
}
