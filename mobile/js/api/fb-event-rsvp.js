/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import {
  AccessToken,
  GraphRequest,
  GraphRequestManager,
  LoginManager,
} from 'react-native-fbsdk';
import { performRequest } from './fb';
import { OkCancelAlert } from '../ui';

export default class RsvpOnFB {
  static RSVPs = ['attending', 'maybe', 'declined'];

  static async getPermissionsAndTryAgain(eventId, rsvpApiValue) {
    // Need to prime the user before switching apps and asking for "more" permissions
    await OkCancelAlert(
      'RSVP Permissions',
      'To RSVP to this event, you need to give DanceDeets access to your Facebook event RSVPs.'
    );

    const result = await LoginManager.logInWithPublishPermissions([
      'rsvp_event',
    ]);
    if (result.isCancelled) {
      throw new Error('Request for RSVP Permission was Cancelled');
    } else {
      // try again!
      return RsvpOnFB.send(eventId, rsvpApiValue);
    }
  }

  static async send(eventId: string, rsvpApiValue: string) {
    try {
      const path = `${eventId}/${rsvpApiValue}`;
      const result = await performRequest('POST', path);
      return result;
    } catch (error) {
      if (error.code === '403' || error.code === 'ECOM.FACEBOOK.SDK.CORE8') {
        return await RsvpOnFB.getPermissionsAndTryAgain(eventId, rsvpApiValue);
      } else {
        throw error;
      }
    }
  }

  static getRsvpIndex(eventId: string) {
    return new Promise(async (resolve, reject) => {
      const accessToken = await AccessToken.getCurrentAccessToken();
      if (accessToken == null) {
        throw new Error('No access token');
      }
      const graphManager = new GraphRequestManager();
      RsvpOnFB.RSVPs.forEach((apiValue, index) => {
        const path = `${eventId}/${apiValue}/${accessToken.userID}`;
        const request = new GraphRequest(
          path,
          { parameters: { fields: { string: 'id' } } },
          (error: ?Object, result: ?Object) => {
            if (error) {
              reject(error);
            } else if (result && result.data.length > 0) {
              resolve(index);
            }
          }
        );
        graphManager.addRequest(request);
      });
      graphManager.addBatchCallback((error: ?Object, result: ?Object) => {
        // If we haven't already called resolve(),
        // let's call it now with "unknown" as our result.
        // if it was called, then this result will be ignored.
        resolve(-1);
      });
      graphManager.start();
    });
  }
}
