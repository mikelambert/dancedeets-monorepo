/**
 * Copyright 2016 DanceDeets.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

export async function hasSkippedLogin(): Promise<boolean> {
  const result = await AsyncStorage.getItem('login.skipped');
  if (result !== null) {
    return result === '1';
  }
  return false;
}

export async function setSkippedLogin(skipped: boolean = true): Promise<void> {
  await AsyncStorage.setItem('login.skipped', skipped ? '1' : '0');
}
