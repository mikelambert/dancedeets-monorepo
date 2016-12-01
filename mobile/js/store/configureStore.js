/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { applyMiddleware, createStore } from 'redux';
import thunk from 'redux-thunk';
import createLogger from 'redux-logger';
import promise from './promise';
import array from './array';
import analytics from './analytics';
import reducers from '../reducers';

const isDebuggingInChrome = __DEV__ && !!window.navigator.userAgent;

const logger = createLogger({
  predicate: (getState, action) => isDebuggingInChrome,
  collapsed: true,
  duration: true,
});

const createStoreWithMiddleware = applyMiddleware(thunk, promise, array, analytics, logger)(createStore);

export default function configureStore() {
  const store = createStoreWithMiddleware(reducers);
  if (isDebuggingInChrome) {
    window.store = store;
  }
  return store;
}
