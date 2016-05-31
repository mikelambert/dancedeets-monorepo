/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

export type AddEventData = {
  // From FB (by way of DanceDeets)
  id: string;
  name: string;
  start_time: string;
  host: string;
  rsvp_status: string;

  // From DanceDeets
  loaded: boolean;

  // From our app:
  pending: ?boolean;
};

export type AddEventList = Array<AddEventData>;

export type SortOrder = 'ByDate' | 'ByName';
