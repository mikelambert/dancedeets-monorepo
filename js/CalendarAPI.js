/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import {
  Alert,
  Linking,
  Platform,
} from 'react-native';
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

function OkAlert(title: string, message: string, cancel = false): Promise {
  return new Promise((resolve, reject) => {
    var buttons = [];
    if (cancel) {
      buttons.push({text: 'Cancel', onPress: () => reject(), style: 'cancel'});
    }
    buttons.push({text: 'OK', onPress: () => resolve()});
    Alert.alert(title, message, buttons);
  });
}

function OkCancelAlert(title: string, message: string): Promise {
  return OkAlert(title, message, true);
}

async function addIOS(event: Event) {
  var status = await authorizationStatus();
  status = 'undetermined';
  if (status === 'undetermined') {
    try {
      await OkCancelAlert('Add to Calendar', 'To add this event to your calendar, you need to allow access to your calendar.');
      status = await authorizeEventStore();
    } catch (error) {}
  }

  if (status != 'authorized') {
    if (status === 'restricted') {
      OkAlert('Cannot Access Calendar', 'Could not access calendar.');
    } else if (status === 'denied') {
      try {
        await OkCancelAlert('Cannot Access Calendar', 'Please open Settings to allow Calendar permissions.');
        Linking.openURL('app-settings:');
      } catch (err) {}
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
    notes: event.description, // TODO: add url!
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
