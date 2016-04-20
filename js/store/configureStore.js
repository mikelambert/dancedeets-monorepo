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
import {persistStore, autoRehydrate} from 'redux-persist';
import {AsyncStorage} from 'react-native';

var isDebuggingInChrome = __DEV__ && !!window.navigator.userAgent;

var logger = createLogger({
  predicate: (getState, action) => isDebuggingInChrome,
  collapsed: true,
  duration: true,
});

var createStoreWithMiddleware = applyMiddleware(thunk, promise, array, analytics, logger)(createStore);

export default function configureStore(onComplete: ?() => void) {
  // TODO(frantic): reconsider usage of redux-persist, maybe add cache breaker
  // Create a fresh store:
  const store = createStoreWithMiddleware(reducers);
  // const store = autoRehydrate()(createStoreWithMiddleware)(reducers);
  persistStore(store, {storage: AsyncStorage}, onComplete);
  if (isDebuggingInChrome) {
    window.store = store;
  }
  return store;
}
