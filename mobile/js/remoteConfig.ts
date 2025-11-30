/**
 * Copyright 2016 DanceDeets.
 *
 * Firebase Remote Config - modular API
 */

import remoteConfig from '@react-native-firebase/remote-config';

async function loadConfig(): Promise<void> {
  // Set minimum fetch interval for development
  if (__DEV__) {
    await remoteConfig().setConfigSettings({
      minimumFetchIntervalMillis: 0, // Allow fetching anytime in dev
    });
  }
  // Fetch and activate in one call
  await remoteConfig().fetchAndActivate();
}

loadConfig();

export async function get<T>(value: string): Promise<T | null> {
  const result = remoteConfig().getValue(value);
  if (result && result.asString()) {
    return JSON.parse(result.asString()) as T;
  }
  return null;
}
