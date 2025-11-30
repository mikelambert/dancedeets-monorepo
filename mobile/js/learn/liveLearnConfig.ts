/**
 * Copyright 2016 DanceDeets.
 */

import remoteConfig from '@react-native-firebase/remote-config';

// eslint-disable-next-line no-unused-vars
async function loadConfig() {
  if (__DEV__) {
    await remoteConfig().setConfigSettings({
      minimumFetchIntervalMillis: 0,
    });
  }
  await remoteConfig().fetch();
  await remoteConfig().activate();
}

// loadConfig();

export async function getRemoteBlogs(): Promise<any> {
  const result = remoteConfig().getValue('Learn:blogs');
  if (result) {
    return JSON.parse(result.asString());
  }
}
