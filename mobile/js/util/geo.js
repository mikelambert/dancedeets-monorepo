/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import type { Address } from '../events/formatAddress';
import { Platform } from 'react-native';
import Geocoder from '../api/geocoder';
import { format } from '../events/formatAddress';
import Permissions from 'react-native-permissions';

function getCurrentPosition() {
  return new Promise((resolve, reject) => {
    const highAccuracy = Platform.OS == 'ios';
    navigator.geolocation.getCurrentPosition(resolve, reject,
      {enableHighAccuracy: highAccuracy, timeout: 10 * 1000, maximumAge: 10 * 60 * 1000}
    );
  });
}

export async function getPosition() {
//  Permissions.openSettings();
  if (Platform.OS === 'ios') {
    const status = await Permissions.requestPermission('location');
    if (status !== 'authorized') {
      // No location permission. Let's ignore it for now since the app will work fine
      // But if we ever change our mind, we can prompt and run:
      // Permissions.openSettings();
      throw new Error('No location permissions');
    }
    // Otherwise have authorized permissions now, let's get their location!
  }
  return await getCurrentPosition();
}

export async function getAddress() {
  if (Platform.OS === 'ios') {
    const status = await Permissions.requestPermission('location');
    if (status !== 'authorized') {
      // No location permission. Let's ignore it for now since the app will work fine
      // But if we ever change our mind, we can prompt and run:
      // Permissions.openSettings();
      return '';
    }
    // Otherwise have authorized permissions now, let's get their location!
  }
  // This has atimeout, so we need to do the user action (requesting permissions) above
  // to ensure this call doesn't unnecessarily time out.
  const position = await getPosition();
  const newCoords = { lat: position.coords.latitude, lng: position.coords.longitude };
  const address: Address = await Geocoder.geocodePosition(newCoords);
  const formattedAddress = format(address[0]);
  return formattedAddress;
}
