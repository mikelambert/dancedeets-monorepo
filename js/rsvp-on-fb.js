/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import {
  GraphRequest,
  GraphRequestManager,
  LoginManager,
} from 'react-native-fbsdk';

export default class RsvpOnFB {

  async send(eventId: string, rsvpApiValue: string) {
    try {
      const result = await this.sendRsvp(eventId, rsvpApiValue);
      return result;
    } catch (error) {
      if (error.code === '403') {
        const result = await LoginManager.logInWithPublishPermissions(['rsvp_event']);
        if (result.isCancelled) {
          throw 'Request for RSVP Permission was Cancelled';
        } else {
          // try again!
          return this.send(eventId, rsvpApiValue);
        }
      } else {
        throw error;
      }
    }
  }

  sendRsvp(eventId: string, rsvpApiValue: string) {
    const f = function (resolve, reject) {
      const rsvpRequest = new GraphRequest(
        '/' + eventId + '/' + rsvpApiValue,
        {httpMethod: 'POST'},
        function(error: ?Object, result: ?Object) {
          if (error) {
            reject(error);
          } else {
            resolve(result);
          }
        }
      );
      new GraphRequestManager().addRequest(rsvpRequest).start();
    };
    return new Promise(f.bind(this));
  }

  async get(eventId: string) {
    return 'maybe';
  }
}
