/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as addEvents from './addEvents';
import * as appNavigation from './appNavigation';
import * as firebase from './firebase';
import * as loadedEvents from './loadedEvents';
import * as login from './login';
import * as loginComplex from './loginComplex';
import * as search from './search';
import * as translate from './translate';
import * as tutorials from './tutorials';
import * as searchHeader from '../ducks/searchHeader';
import * as searchQuery from '../ducks/searchQuery';

module.exports = {
  ...addEvents,
  ...appNavigation,
  ...firebase,
  ...loadedEvents,
  ...login,
  ...loginComplex,
  ...search,
  ...searchHeader,
  ...searchQuery,
  ...translate,
  ...tutorials,
};
