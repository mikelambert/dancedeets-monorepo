/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {
  AsyncStorage,
} from 'react-native';

export async function getPreference(key: string, defaultValue: boolean): Promise<boolean> {
  const result = await AsyncStorage.getItem('preferences.notifications.' + key);
  if (result !== null) {
    return result === '1';
  }
  return defaultValue;
}

export async function setPreference(key: string, value: boolean) {
  await AsyncStorage.setItem('preferences.notifications.' + key, value ? '1' : '0');
}
