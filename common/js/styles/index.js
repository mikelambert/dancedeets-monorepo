/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

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

export type Style = {
  id: string;
  title: string;
  imageName: string;
  width: number;
  height: number;
};

export default {
  break: {
    id: 'break',
    title: 'Bboy / Bgirl',
    imageName: 'break.png',
    width: 505,
    height: 512,
  },
  hiphop: {
    id: 'hiphop',
    title: 'Hip-Hop',
    imageName: 'hiphop.png',
    width: 278,
    height: 512,
  },
  pop: {
    id: 'pop',
    title: 'Popping',
    imageName: 'pop.png',
    width: 283,
    height: 512,
  },
  lock: {
    id: 'lock',
    title: 'Locking',
    imageName: 'lock.png',
    width: 339,
    height: 512,
  },
  house: {
    id: 'house',
    title: 'House Dance',
    imageName: 'house.png',
    width: 381,
    height: 512,
  },
  krump: {
    id: 'krump',
    title: 'Krump',
    imageName: 'krump.png',
    width: 420,
    height: 512,
  },
  other: {
    id: 'other',
    title: 'Other Styles',
    titleMessage: messages.otherStylesTitle,
    imageName: 'other.png',
    width: 312,
    height: 512,
  },
};
