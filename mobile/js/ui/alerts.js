/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
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
      // TODO(localization)
      buttons.push({
        text: 'Cancel',
        onPress: () => reject(),
        style: 'cancel',
      });
    }
    // TODO(localization)
    buttons.push({ text: 'OK', onPress: () => resolve() });
    Alert.alert(title, message, buttons);
  });
}

export function OkCancelAlert(title: string, message: string): Promise<void> {
  return OkAlert(title, message, true);
}
