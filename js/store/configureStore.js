/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {applyMiddleware, createStore} from 'redux';
import thunk from 'redux-thunk';
import promise from './promise';
import array from './array';
import analytics from './analytics';
import reducers from '../reducers';
import createLogger from 'redux-logger';

var isDebuggingInChrome = __DEV__ && !!window.navigator.userAgent;

var logger = createLogger({
  predicate: (getState, action) => isDebuggingInChrome,
  collapsed: true,
  duration: true,
});

var createStoreWithMiddleware = applyMiddleware(thunk, promise, array, analytics, logger)(createStore);

export default function configureStore() {
  const store = createStoreWithMiddleware(reducers);
  if (isDebuggingInChrome) {
    window.store = store;
  }
  return store;
}
