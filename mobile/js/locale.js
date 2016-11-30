/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import Locale from 'react-native-locale';
import {
  supportedLocales,
  defaultLocale,
} from 'dancedeets-common/intl';

export const getCurrentLocale = () => {
  const currentLocale = Locale.constants().localeIdentifier.split('_')[0];
  return supportedLocales.indexOf(currentLocale) !== -1
    ? currentLocale
    : defaultLocale;
};
