/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import {
  defineMessages,
} from 'react-intl';

export default defineMessages({
  numTutorials: {
    id: 'tutorialVideos.numTutorials',
    defaultMessage: '{count,number} Tutorials',
    description: 'How many tutorials there are',
  },
  totalTime: {
    id: 'tutorialVideos.totalTime',
    defaultMessage: 'Total: {time}',
    description: 'Total time for all tutorials',
  },
  chooseStyle: {
    id: 'tutorialVideos.styleHeader',
    defaultMessage: 'What style do you want to learn today?',
    description: 'Header for styles list',
  },
  chooseTutorial: {
    id: 'tutorialVideos.tutorialHeader',
    defaultMessage: 'What do you want to learn today?',
    description: 'Header for tutorials list',
  },
  numVideosWithDuration: {
    id: 'tutorialVideos.numVideosWithDuration',
    defaultMessage: '{count,number} videos: {duration}',
    description: 'Total for all videos in a tutorial',
  },
  tutorialFooter: {
    id: 'tutorialVideos.turorialFooter',
    defaultMessage: 'Want to put your tutorials, DVD, or classes here?\nWant lessons from the world\'s best teachers?\n',
    description: 'Footer for tutorials list, inviting participation',
  },
  contact: {
    id: 'tutorialVideos.contact',
    defaultMessage: 'Contact Us',
    description: '"Contact Us" button for asking about tutorials',
  },
  contactSuffix: {
    id: 'tutorialVideos.contactSuffix',
    defaultMessage: ' and let us know!',
    description: 'Suffix to display after the "Contact Us" button',
  },
  languagePrefixedTitle: {
    id: 'tutorialVideos.languagePrefixedTitle',
    defaultMessage: '{language}: {title}',
    description: 'When we have a foreign language tutorial, we prefix that language to the title',
  },
  timeHoursMinutes: {
    id: 'tutorialVideos.timeHoursMinutes',
    defaultMessage: '{hours,number}h {minutes,number}m',
    description: 'Time formatting',
  },
  timeMinutes: {
    id: 'tutorialVideos.timeMinutes',
    defaultMessage: '{minutes,number}m',
    description: 'Time formatting',
  },
  timeSeconds: {
    id: 'tutorialVideos.timeSeconds',
    defaultMessage: '{seconds,number}s',
    description: 'Time formatting',
  },
});
