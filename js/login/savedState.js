/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {
  AsyncStorage,
} from 'react-native';

export async function hasSkippedLogin() {
  const result = await AsyncStorage.getItem('login.skipped');
  if (result !== null) {
    return result === '1';
  }
  return false;
}

export async function setSkippedLogin(skipped: boolean = true) {
  await AsyncStorage.setItem('login.skipped', skipped ? '1' : '0');
}
