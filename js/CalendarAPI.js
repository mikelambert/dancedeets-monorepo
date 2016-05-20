/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { Platform } from 'react-native';
import CalendarEventsIOS from 'react-native-calendar-events';
import { Event } from './events/models';
import moment from 'moment';

function authorizationStatus(): Promise {
  return new Promise((resolve, reject) => {
    CalendarEventsIOS.authorizationStatus((x) => {
      resolve(x.status);
    });
  });
}

function authorizeEventStore(): Promise {
  return new Promise((resolve, reject) => {
    CalendarEventsIOS.authorizeEventStore((x) => {
      resolve(x.status);
    });
  });
}

async function addIOS(event: Event) {
  var status = await authorizationStatus();
  if (status === 'undetermined') {
    // TODO: priming for features!
    status = await authorizeEventStore();
  }

  if (status != 'authorized') {
    if (status === 'restricted') {
      // TODO: error
    } else if (status === 'denied') {
      // TODO: error, go to settings!
    }
    return;
  }

  // Parse dates-with-timezones, and use them to construct an event
  var start = moment(event.start_time, moment.ISO_8601);
  var end = moment(event.end_time, moment.ISO_8601);
  if (!end) {
    end = start.add(1.5, 'hours');
  }
  CalendarEventsIOS.saveEvent(event.name, {
    location: event.venue.fullAddress(),
    notes: event.description,
    startDate: start.toISOString(),
    endDate: end ? end.toISOString() : null,
  });

  // TODO: added!
}

export function add(event: Event) {
  if (Platform.OS == 'ios') {
    addIOS(event);
  } else {
    //TODO: implement
  }
}
