/**
 * Copyright 2016 DanceDeets.
 */

import { applyMiddleware, createStore, Store } from 'redux';
import thunk from 'redux-thunk';
import { createLogger } from 'redux-logger';
import promise from './promise';
import array from './array';
import analytics from './analytics';
import reducers from '../reducers';
import type { RootState, Action } from '../actions/types';

// Declare global window for React Native Chrome debugging
declare const window: any;

const isDebuggingInChrome = __DEV__ && !!window?.navigator?.userAgent;

const logger = createLogger({
  predicate: (getState: () => RootState, action: Action) => isDebuggingInChrome,
  collapsed: true,
  duration: true,
});

const createStoreWithMiddleware = applyMiddleware(
  thunk,
  promise,
  array,
  analytics,
  logger
)(createStore);

export default function configureStore(): Store<RootState, Action> {
  const store = createStoreWithMiddleware(reducers);
  if (isDebuggingInChrome) {
    (window as any).store = store;
  }
  return store;
}
