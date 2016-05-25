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

export function performRequest(method: string, path: string) {
  return new Promise((resolve, reject) => {
    const request = new GraphRequest(
      path,
      {httpMethod: method},
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
