/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { Alert, Platform } from 'react-native';
import Permissions from 'react-native-permissions';
import CalendarEventsIOS from 'react-native-calendar-events';
import SendIntentAndroid from 'react-native-send-intent';
import moment from 'moment';
import { Event } from 'dancedeets-common/js/events/models';
import { OkAlert, OkCancelAlert } from '../ui';

function getDescription(event: Event): string {
  return `${event.getUrl()}\n\n${event.description}`;
}

function getStartEndTime(event: Event) {
  // Parse dates-with-timezones, and use them to construct an event
  const start = moment(event.start_time, moment.ISO_8601);
  let end = null;
  if (event.end_time) {
    end = moment(event.end_time, moment.ISO_8601);
  } else {
    end = start.add(1.5, 'hours');
  }
  return { start, end };
}

async function addIOS(event: Event) {
  let status = await CalendarEventsIOS.authorizationStatus();

  if (status === 'undetermined') {
    try {
      // TODO(localization)
      await OkCancelAlert(
        'Add to Calendar',
        'To add this event to your calendar, you need to allow access to your calendar.'
      );
      status = await CalendarEventsIOS.authorizeEventStore();
    } catch (error) {
      console.log('Canceled: Add to Calendar');
      return false;
    }
  }

  if (status !== 'authorized') {
    if (status === 'restricted') {
      OkAlert('Cannot Access Calendar', 'Could not access calendar.');
      return false;
    } else if (status === 'denied') {
      try {
        // TODO(localization)
        await OkCancelAlert(
          'Cannot Access Calendar',
          'Please open Settings to allow Calendar permissions.'
        );
        if (await Permissions.canOpenSettings()) {
          Permissions.openSettings();
        }
      } catch (err) {
        console.log('Canceled: Add to Calendar Permissions');
      }
    }
    return false;
  }

  const { start, end } = getStartEndTime(event);

  try {
    CalendarEventsIOS.saveEvent(event.name, {
      location: event.venue.fullAddress(),
      notes: getDescription(event),
      startDate: start.toISOString(),
      endDate: end.toISOString(),
      url: event.getUrl(),
    });
  } catch (e) {
    console.warn(e);
  }

  return true;
}

function androidDate(date: Date) {
  // 2016-01-01 01:00
  const tzOffset = new Date().getTimezoneOffset() * 60000;
  try {
    return new Date(date - tzOffset)
      .toISOString()
      .replace(/T/, ' ')
      .slice(0, 16);
  } catch (e) {
    throw new Error(
      `Date: new Date(${date.toString()} - ${tzOffset}) returned invalid date`
    );
  }
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
  return true;
}

export async function add(event: Event) {
  if (Platform.OS === 'ios') {
    return await addIOS(event);
  } else {
    return addAndroid(event);
  }
}
