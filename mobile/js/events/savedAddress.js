/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { AsyncStorage } from 'react-native';

const key = 'location.lastSearch';

export async function loadSavedAddress() {
  const result = (await AsyncStorage.getItem(key)) || '';
  return result;
}

export async function storeSavedAddress(address: string) {
  await AsyncStorage.setItem(key, address || '');
}
