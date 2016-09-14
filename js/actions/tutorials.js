/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type { Action } from './types';

export function setTutorialVideoIndex(index: number): Action {
  return {
    type: 'TUTORIAL_SET_VIDEO_INDEX',
    index,
  };
}
