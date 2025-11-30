/**
 * Copyright 2016 DanceDeets.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const key = 'location.lastSearch';

export async function loadSavedAddress(): Promise<string> {
  const result = (await AsyncStorage.getItem(key)) || '';
  return result;
}

export async function storeSavedAddress(address: string): Promise<void> {
  await AsyncStorage.setItem(key, address || '');
}
