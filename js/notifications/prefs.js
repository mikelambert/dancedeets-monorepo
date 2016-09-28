/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {
  AsyncStorage,
} from 'react-native';

export async function getPreference(key: string, defaultValue: any) {
  const result = await AsyncStorage.getItem('preferences.notifications.' + key);
  if (result !== null) {
    return result;
  }
  return defaultValue;
}

export async function setPreference(key: string, value: any) {
  await AsyncStorage.setItem('preferences.notifications.' + key, value);
}
