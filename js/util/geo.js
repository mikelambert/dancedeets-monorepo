/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import type { Address } from '../events/formatAddress';
import { Platform } from 'react-native';
import Geocoder from '../api/geocoder';
import { format } from '../events/formatAddress';

export function getPosition() {
  return new Promise((resolve, reject) => {
    const highAccuracy = Platform.OS == 'ios';
    navigator.geolocation.getCurrentPosition(resolve, reject,
      {enableHighAccuracy: highAccuracy, timeout: 10 * 1000, maximumAge: 10 * 60 * 1000}
    );
  });
}

export async function getAddress() {
  const position = await getPosition();
  const newCoords = { lat: position.coords.latitude, lng: position.coords.longitude };
  const address: Address = await Geocoder.geocodePosition(newCoords);
  const formattedAddress = format(address[0]);
  return formattedAddress;
}
