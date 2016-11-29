/**
 * Copyright 2016 DanceDeets.
 * @flow
 */

import Geocoder from 'react-native-geocoder';
import { googleKey } from '../keys';

Geocoder.fallbackToGoogle(googleKey);

export default Geocoder;
