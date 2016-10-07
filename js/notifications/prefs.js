/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {
  AsyncStorage,
} from 'react-native';

export const PreferenceNames = {
  overall: 'overall',
  sounds: 'sounds',
  vibration: 'vibration',
};

export async function getPreference(key: string, defaultValue: boolean): Promise<boolean> {
  if (key == null) {
    throw new Error('Need key for getPreference');
  }
  const result = await AsyncStorage.getItem('preferences.notifications.' + key);
  if (result !== null) {
    return result === '1';
  }
  return defaultValue;
}

export async function setPreference(key: string, value: boolean) {
  if (key == null) {
    throw new Error('Need key for setPreference');
  }
  await AsyncStorage.setItem('preferences.notifications.' + key, value ? '1' : '0');
}
