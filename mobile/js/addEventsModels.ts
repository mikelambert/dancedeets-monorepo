/**
 * Copyright 2016 DanceDeets.
 */

export interface AddEventData {
  // From FB (by way of DanceDeets)
  id: string;
  name: string;
  start_time: string;
  host: string;
  rsvp_status: string;

  // From DanceDeets
  loaded: boolean;

  // From our app:
  pending?: boolean;
  clickedConfirming?: boolean;
}

export type AddEventList = AddEventData[];

export type SortOrder = 'ByDate' | 'ByName';
