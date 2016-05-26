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
import SendIntentAndroid from 'react-native-send-intent';
import { Event } from '../events/models';
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

function getDescription(event: Event): string {
  return event.getUrl() + '\n\n' + event.description;
}

function getStartEndTime(event: Event) {
  // Parse dates-with-timezones, and use them to construct an event
  var start = moment(event.start_time, moment.ISO_8601);
  var end = moment(event.end_time, moment.ISO_8601);
  if (!end) {
    end = start.add(1.5, 'hours');
  }
  return { start, end };
}

async function addIOS(event: Event) {
  var status = await authorizationStatus();

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
    return false;
  }

  const { start, end } = getStartEndTime(event);

  CalendarEventsIOS.saveEvent(event.name, {
    location: event.venue.fullAddress(),
    notes: getDescription(event),
    startDate: start.toISOString(),
    endDate: end ? end.toISOString() : null,
  });

  return true;
}

function androidDate(date: Date) {
  // 2016-01-01 01:00
  const tzOffset = new Date().getTimezoneOffset() * 60000;
  return new Date(date - tzOffset).toISOString().replace(/T/, ' ').slice(0, 16);
}

function addAndroid(event: Event) {
  const { start, end } = getStartEndTime(event);

  SendIntentAndroid.addCalendarEvent({
    title: event.name,
    description: getDescription(event),
    startDate: androidDate(start),
    endDate: androidDate(end),
    location: event.venue.fullAddress(),
    recurrence: '',
  });
}
export function add(event: Event) {
  if (Platform.OS == 'ios') {
    return addIOS(event);
  } else {
    return addAndroid(event);
  }
}
