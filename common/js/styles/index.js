/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { defineMessages } from 'react-intl';

// Copied from react-intl, though we don't want a dependency on the full thing just for type-checking
type messageDescriptorPropTypes = {
  id: string,
  description?: string,
  defaultMessage?: string,
};

export const messages = defineMessages({
  otherStylesTitle: {
    id: 'tutorialVideos.otherStylesTitle',
    defaultMessage: 'Other Styles',
    description: 'Name of the tutorial category for miscellaneous dance styles',
  },
  pop: {
    id: 'styles.pop',
    defaultMessage: 'Popping',
    description: 'Dance style',
  },
  break: {
    id: 'styles.break',
    defaultMessage: 'Bboy / Bgirl',
    description: 'Dance style',
  },
  house: {
    id: 'styles.house',
    defaultMessage: 'House',
    description: 'Dance style',
  },
  hiphop: {
    id: 'styles.hiphop',
    defaultMessage: 'Hip-Hop',
    description: 'Dance style',
  },
  lock: {
    id: 'styles.lock',
    defaultMessage: 'Locking',
    description: 'Dance style',
  },
  krump: {
    id: 'styles.krump',
    defaultMessage: 'Krump',
    description: 'Dance style',
  },
  soul: {
    id: 'styles.soul',
    defaultMessage: 'Soul Dance',
    description: 'Dance style',
  },
  waack: {
    id: 'styles.waack',
    defaultMessage: 'Waacking',
    description: 'Dance style',
  },
  bebop: {
    id: 'styles.bebop',
    defaultMessage: 'Bebop / Jazz Fusion',
    description: 'Dance style',
  },
  dougie: {
    id: 'styles.dougie',
    defaultMessage: 'Dougie',
    description: 'Dance style',
  },
  dance: {
    id: 'styles.dance',
    defaultMessage: 'Basic Dance',
    description: 'Dance style',
  },
  misc: {
    id: 'styles.misc',
    defaultMessage: 'Miscellaneous',
    description: 'Dance style',
  },
  streetjazz: {
    id: 'styles.streetjazz',
    defaultMessage: 'Street Jazz',
    description: 'Dance style',
  },
  dancehall: {
    id: 'styles.dancehall',
    defaultMessage: 'Dancehall',
    description: 'Dance style',
  },
  electro: {
    id: 'styles.electro',
    defaultMessage: 'Electro Dance',
    description: 'Dance style',
  },
  flex: {
    id: 'styles.flex',
    defaultMessage: 'Flexing',
    description: 'Dance style',
  },
});

export type Style = {
  id: string,
  title: string,
  titleMessage?: messageDescriptorPropTypes,
  imageName: string,
  width: number,
  height: number,
};

export default {
  break: {
    id: 'break',
    title: 'Bboy / Bgirl',
    titleMessage: messages.break,
    imageName: 'break.png',
    width: 505,
    height: 512,
  },
  hiphop: {
    id: 'hiphop',
    title: 'Hip-Hop',
    titleMessage: messages.hiphop,
    imageName: 'hiphop.png',
    width: 278,
    height: 512,
  },
  pop: {
    id: 'pop',
    title: 'Popping',
    titleMessage: messages.pop,
    imageName: 'pop.png',
    width: 283,
    height: 512,
  },
  lock: {
    id: 'lock',
    title: 'Locking',
    titleMessage: messages.lock,
    imageName: 'lock.png',
    width: 339,
    height: 512,
  },
  house: {
    id: 'house',
    title: 'House Dance',
    titleMessage: messages.house,
    imageName: 'house.png',
    width: 381,
    height: 512,
  },
  krump: {
    id: 'krump',
    title: 'Krump',
    imageName: 'krump.png',
    titleMessage: messages.krump,
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
