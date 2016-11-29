/*
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */
'use strict';

import {
  GraphRequest,
  GraphRequestManager,
} from 'react-native-fbsdk';

export function performRequest(method: string, path: string, params: Object = {}) {
  const newParams = Object.assign({}, params);
  // Jump through hoops to setup the calling convention react-native-fbsdk wants
  Object.keys(newParams).forEach((k) => { newParams[k] = {string: newParams[k]}; });
  return new Promise((resolve, reject) => {
    const request = new GraphRequest(
      path,
      {
        httpMethod: method,
        parameters: newParams,
      },
      function(error: ?Object, result: ?Object) {
        if (error) {
          reject(error);
        } else if (result == null) {
          reject('Empty result');
        } else {
          resolve(result);
        }
      }
    );
    new GraphRequestManager().addRequest(request).start();
  });
}
