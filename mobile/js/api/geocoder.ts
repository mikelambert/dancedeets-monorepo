/**
 * Copyright 2016 DanceDeets.
 */

import Geocoder from 'react-native-geocoder';
import { googleKey } from '../keys';

Geocoder.fallbackToGoogle(googleKey);

export default Geocoder;
