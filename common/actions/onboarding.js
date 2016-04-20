/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import type { Action } from './types';

export function loginTutorialNoLogin(): Action {
  return {
    type: 'ONBOARD_NO_LOGIN',
  };
}

export function loginTutorialStillNoLogin(): Action {
  return {
    type: 'ONBOARD_STILL_NO_LOGIN',
  };
}
