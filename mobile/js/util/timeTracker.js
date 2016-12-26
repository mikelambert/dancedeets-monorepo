/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import {
  track,
  trackStart,
} from '../store/track';

export function tabTimeStart(tab: string) {
  trackStart(`Tab Time ${tab}`);
}

export function tabTimeEnd(tab: string) {
  track(`Tab Time ${tab}`); // Can't use track() properties
}

