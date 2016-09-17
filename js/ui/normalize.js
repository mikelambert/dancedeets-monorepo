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

export function semiNormalize(size: number): number {
  return Math.round(size + 0.4 * (normalize(size) - size));
}
