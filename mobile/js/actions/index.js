/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as addEvents from './addEvents';
import * as appNavigation from './appNavigation';
import * as firebase from './firebase';
import * as login from './login';
import * as loginComplex from './loginComplex';
import * as search from './search';
import * as translate from './translate';
import * as tutorials from './tutorials';
import * as searchHeader from '../ducks/searchHeader';

module.exports = {
  ...addEvents,
  ...appNavigation,
  ...firebase,
  ...login,
  ...loginComplex,
  ...search,
  ...searchHeader,
  ...translate,
  ...tutorials,
};
