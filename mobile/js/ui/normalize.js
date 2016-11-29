/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { Dimensions } from 'react-native';


const scale = Dimensions.get('window').width / 375;

export function normalize(size: number): number {
  return Math.round(scale * size);
}

export function semiNormalize(size: number, scalingSpeed: number = 0.4): number {
  return Math.round(size + scalingSpeed * (normalize(size) - size));
}
