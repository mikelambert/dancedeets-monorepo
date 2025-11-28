/**
 * Copyright 2016 DanceDeets.
 */

import { Alert, Platform } from 'react-native';

export function OkAlert(
  title: string,
  message: string,
  cancel: boolean = false
): Promise<void> {
  return new Promise((resolve, reject) => {
    const buttons = [];
    if (cancel) {
      buttons.push({
        text: 'Cancel',
        onPress: () => reject(),
        style: 'cancel' as const,
      });
    }
    buttons.push({ text: 'OK', onPress: () => resolve() });
    Alert.alert(title, message, buttons);
  });
}

export function OkCancelAlert(title: string, message: string): Promise<void> {
  return OkAlert(title, message, true);
}
