/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {
  defineMessages,
} from 'react-intl';

const messages = defineMessages({
  otherStylesTitle: {
    id: 'tutorialVideos.otherStylesTitle',
    defaultMessage: 'Other Styles',
    description: 'Name of the tutorial category for miscellaneous dance styles',
  },
});

export default {
  break: {
    title: 'Bboy / Bgirl',
    thumbnail: require('./images/break.png'),
  },
  hiphop: {
    title: 'Hip-Hop',
    thumbnail: require('./images/hiphop.png'),
  },
  pop: {
    title: 'Popping',
    thumbnail: require('./images/pop.png'),
  },
  lock: {
    title: 'Locking',
    thumbnail: require('./images/lock.png'),
  },
  house: {
    title: 'House Dance',
    thumbnail: require('./images/house.png'),
  },
  krump: {
    title: 'Krump',
    thumbnail: require('./images/krump.png'),
  },
  other: {
    title: 'Other Styles',
    titleMessage: messages.otherStylesTitle,
    thumbnail: require('./images/other.png'),
  },
};
