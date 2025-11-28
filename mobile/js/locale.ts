/**
 * Copyright 2016 DanceDeets.
 */

import Locale from 'react-native-locale';

export const getCurrentLocale = (): string =>
  Locale.constants().localeIdentifier.replace('_', '-');
