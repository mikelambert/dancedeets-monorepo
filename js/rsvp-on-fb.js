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
  eventId: string;
  rsvpApiValue: string;

  constructor(eventId: string, rsvpApiValue: string) {
    this.eventId = eventId;
    this.rsvpApiValue = rsvpApiValue;
  }

  async send() {
    try {
      const result = await this.sendRsvp();
      return result;
    } catch (error) {
      console.log('error', error);
      if (error.code === '403') {
        const result = await LoginManager.logInWithPublishPermissions(['rsvp_event']);
        if (result.isCancelled) {
          throw 'Request for RSVP Permission was Cancelled';
        } else {
          // try again!
          return this.send();
        }
      } else {
        throw error;
      }
    }
  }

  sendRsvp() {
    const f = function (resolve, reject) {
      const rsvpRequest = new GraphRequest(
        '/' + this.eventId + '/' + this.rsvpApiValue,
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
}
