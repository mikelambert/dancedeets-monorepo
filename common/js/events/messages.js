/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { defineMessages } from 'react-intl';

export default defineMessages({
  addToCalendar: {
    id: 'event.addToCalendar',
    defaultMessage: 'Add to Calendar',
    description: "Button to add this event to the user's calendar",
  },
  addedToCalendar: {
    id: 'event.addedToCalendar',
    defaultMessage: 'Added to Calendar',
    description: 'Confirmation message for iOS after adding to the OS calendar',
  },
  translate: {
    id: 'event.translate',
    defaultMessage: 'Translate',
    description: "Button to translate the event into the device's native language",
  },
  untranslate: {
    id: 'event.untranslate',
    defaultMessage: 'Original',
    description: "Button to show the event's original untranslated version",
  },
  addedBy: {
    id: 'event.addedBy',
    defaultMessage: 'Added By: {name}',
    description: 'Describes who added this event to DanceDeets',
  },
  source: {
    id: 'event.source',
    defaultMessage: 'Source:',
    description: 'The original website from which we discovered this event',
  },
  hideOrganizers: {
    id: 'event.hideOrganizers',
    defaultMessage: 'Hide Organizers',
    description: 'Will hide the list of organizers for this event',
  },
  showOrganizers: {
    id: 'event.showOrganizers',
    defaultMessage: 'Show {count, number} Organizers', // Always 2-and-more, so don't need to deal with singular case
    description: 'Will show the list of organizers for this event',
  },
  eventDetails: {
    id: 'event.details',
    defaultMessage: 'Event Details:',
    description: 'Title for the event description card',
  },
  featureRSVP: {
    id: 'feature.RSVP',
    defaultMessage: 'RSVP',
    description: 'The name of the RSVP feature when requesting permissions',
  },
  organizer: {
    id: 'event.organizer',
    defaultMessage: 'Organizer:',
    description: 'Describes the one person who created this event',
  },
  ticketsLink: {
    id: 'event.tickets',
    defaultMessage: 'Tickets:',
    description: 'Link to see/buy tickets for this event',
  },
  attendingCount: {
    id: 'event.attendingCount',
    defaultMessage: '{attendingCount, number} attending',
    description: 'Count of people attending this event',
  },
  attendingMaybeCount: {
    id: 'event.attendingMaybeCount',
    defaultMessage: '{attendingCount, number} attending, {maybeCount, number} maybe',
    description: 'Count of people maybe-attending this event',
  },
  attending: {
    id: 'event.rsvp.attending',
    defaultMessage: "I'll be there!",
    description: 'Clickable text for when a user wants to attend an event',
  },
  maybe: {
    id: 'event.rsvp.maybe',
    defaultMessage: 'I might flake…',
    description: 'Clickable text for when a user wants to attend an event',
  },
  declined: {
    id: 'event.rsvp.declined',
    defaultMessage: 'No thanks.',
    description: 'Clickable text for when a user wants to attend an event',
  },
  milesAway: {
    id: 'distance.miles',
    defaultMessage: '{miles, number} {miles, plural, one {mile} other {miles}} away',
    description: 'Distance of something from the user',
  },
  kmAway: {
    id: 'distance.km',
    defaultMessage: '{km, number} km away',
    description: 'Distance of something from the user',
  },
});
