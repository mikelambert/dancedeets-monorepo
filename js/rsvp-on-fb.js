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
    console.log('a');
    try {
    console.log('b');
      const result = await this.sendRsvp();
      console.log('success', result);
    } catch (error) {
      console.log('error', error);
      if (error.code === '403') {
        try {
          const result = await LoginManager.logInWithPublishPermissions(['rsvp_event']);
          if (result.isCancelled) {
            console.log('canceled!'); // TODO: we need to undo the segmented control!??
          } else {
            // try again!
            return this.send();
          }
        } catch (error2) {
          console.log('error 2', error2);
        }
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
