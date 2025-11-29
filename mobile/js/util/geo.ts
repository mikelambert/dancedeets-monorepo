/**
 * Copyright 2016 DanceDeets.
 *
 * Geolocation utilities with react-native-permissions v4 API
 */

import { Platform } from 'react-native';
import { request, check, PERMISSIONS, RESULTS, openSettings } from 'react-native-permissions';
import Geocoder from '../api/geocoder';
import { format } from '../events/formatAddress';

// Get the appropriate location permission for the platform
const locationPermission = Platform.select({
  ios: PERMISSIONS.IOS.LOCATION_WHEN_IN_USE,
  android: PERMISSIONS.ANDROID.ACCESS_FINE_LOCATION,
  default: PERMISSIONS.IOS.LOCATION_WHEN_IN_USE,
});

interface GeolocationPosition {
  coords: {
    latitude: number;
    longitude: number;
  };
}

// Declare navigator.geolocation for React Native
declare const navigator: {
  geolocation: {
    getCurrentPosition(
      success: (position: GeolocationPosition) => void,
      error?: (error: any) => void,
      options?: { enableHighAccuracy?: boolean; timeout?: number; maximumAge?: number }
    ): void;
  };
};

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
  if (Platform.OS === 'ios') {
    const status = await request(locationPermission);
    if (status !== RESULTS.GRANTED && status !== RESULTS.LIMITED) {
      // No location permission. Let's ignore it for now since the app will work fine
      // But if we ever change our mind, we can prompt and run:
      // openSettings();
      throw new Error('No location permissions');
    }
    // Otherwise have authorized permissions now, let's get their location!
  }
  return await getCurrentPosition();
}

export async function hasLocationPermission(): Promise<boolean> {
  if (Platform.OS === 'ios') {
    const status = await check(locationPermission);
    return status === RESULTS.GRANTED || status === RESULTS.LIMITED;
  } else {
    // Check Android permission status
    const status = await check(locationPermission);
    return status === RESULTS.GRANTED;
  }
}

export async function getAddress(): Promise<string> {
  if (Platform.OS === 'ios') {
    const status = await request(locationPermission);
    if (status !== RESULTS.GRANTED && status !== RESULTS.LIMITED) {
      // No location permission. Let's ignore it for now since the app will work fine
      // But if we ever change our mind, we can prompt and run:
      // openSettings();
      return '';
    }
    // Otherwise have authorized permissions now, let's get their location!
  }
  // This has a timeout, so we need to do the user action (requesting permissions) above
  // to ensure this call doesn't unnecessarily time out.
  const position = await getPosition();
  const newCoords = {
    lat: position.coords.latitude,
    lng: position.coords.longitude,
  };
  const addresses = await Geocoder.geocodePosition(newCoords);
  // GeocodingObject is compatible with Address interface
  const formattedAddress = format(addresses[0] as any);
  return formattedAddress;
}
