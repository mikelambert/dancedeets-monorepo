/*
 * Copyright 2016 DanceDeets.
 */
import { GraphRequest, GraphRequestManager } from 'react-native-fbsdk';

interface GraphError {
  code?: string;
  message?: string;
  [key: string]: any;
}

interface ParameterValue {
  string: string;
}

export function performRequest(
  method: string,
  path: string,
  params: Record<string, any> = {}
): Promise<any> {
  const newParams: Record<string, ParameterValue> = {};
  // Jump through hoops to setup the calling convention react-native-fbsdk wants
  Object.keys(params).forEach(k => {
    newParams[k] = { string: params[k] };
  });
  return new Promise((resolve, reject) => {
    const request = new GraphRequest(
      path,
      {
        httpMethod: method,
        parameters: newParams,
      },
      (error: GraphError | null | undefined, result: any | null | undefined) => {
        if (error) {
          reject(error);
        } else if (result == null) {
          reject(new Error('Empty result'));
        } else {
          resolve(result);
        }
      }
    );
    new GraphRequestManager().addRequest(request).start();
  });
}
