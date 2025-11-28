/**
 * Copyright 2016 DanceDeets.
 */

import { Platform } from 'react-native';
import Permissions from 'react-native-permissions';
import type { Address } from '../events/formatAddress';
import Geocoder from '../api/geocoder';
import { format } from '../events/formatAddress';

const locationPermission = 'location';

interface GeolocationPosition {
  coords: {
    latitude: number;
    longitude: number;
  };
}

function getCurrentPosition(): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    const highAccuracy = Platform.OS === 'ios';
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: highAccuracy,
      timeout: 10 * 1000,
      maximumAge: 10 * 60 * 1000,
    });
  });
}

export async function getPosition(): Promise<GeolocationPosition> {
  //  Permissions.openSettings();
  if (Platform.OS === 'ios') {
    const status = await Permissions.requestPermission(locationPermission);
    if (status !== Permissions.StatusAuthorized) {
      // No location permission. Let's ignore it for now since the app will work fine
      // But if we ever change our mind, we can prompt and run:
      // Permissions.openSettings();
      throw new Error('No location permissions');
    }
    // Otherwise have authorized permissions now, let's get their location!
  }
  return await getCurrentPosition();
}

export async function hasLocationPermission(): Promise<boolean> {
  if (Platform.OS === 'ios') {
    const status = await Permissions.getPermissionStatus(locationPermission);
    return status === Permissions.StatusAuthorized;
  } else {
    // TODO(permissions): The Permissions.getPermissionStatus checks for FINE_LOCATION.
    // So wait until we fetch that new permission, to start using the above code paths.
    return true;
  }
}

export async function getAddress(): Promise<string> {
  if (Platform.OS === 'ios') {
    const status = await Permissions.requestPermission(locationPermission);
    if (status !== Permissions.StatusAuthorized) {
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
  const newCoords = {
    lat: position.coords.latitude,
    lng: position.coords.longitude,
  };
  const address: Address = await Geocoder.geocodePosition(newCoords);
  const formattedAddress = format(address[0]);
  return formattedAddress;
}
