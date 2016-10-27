/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {
  AsyncStorage,
} from 'react-native';

export async function loadSavedAddress() {
  const result = await AsyncStorage.getItem('location.lastSearch') || '';
  return result;
}

export async function storeSavedAddress(address: string) {
  await AsyncStorage.setItem('location.lastSearch', address || '');
}
