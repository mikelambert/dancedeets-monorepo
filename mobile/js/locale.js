/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import Locale from 'react-native-locale';

export const getCurrentLocale = () =>
  Locale.constants().localeIdentifier.replace('_', '-');
