/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { Dimensions } from 'react-native';


const scale = Dimensions.get('window').width / 375;

export default function normalize(size: number): number {
  return Math.round(scale * size);
}
