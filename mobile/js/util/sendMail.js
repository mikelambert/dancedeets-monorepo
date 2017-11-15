/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { Alert, Linking, NativeModules, Platform } from 'react-native';
import querystring from 'querystring';

const Mailer = NativeModules.RNMail;

async function sendGmail(subject, to, body) {
  if (Platform.OS === 'ios') {
    const qs = querystring.stringify({
      subject,
      to,
      body,
    });
    const gmailUrl = `googlegmail:///co?${qs}`;
    if (await Linking.canOpenURL(gmailUrl)) {
      try {
        Linking.openURL(gmailUrl);
        return true;
      } catch (err) {
        console.error(
          'Error opening gmail URL:',
          gmailUrl,
          ', with Error:',
          err
        );
      }
    }
  }
  return false;
}

export default async function sendMail(props: {
  subject: string,
  to: string,
  body: string,
}) {
  const { subject, to, body } = props;
  if (!await sendGmail(subject, to, body)) {
    Mailer.mail(
      {
        subject,
        recipients: [to],
        body,
      },
      (error, event) => {
        if (error) {
          Alert.alert('Error', 'Please email us at feedback@dancedeets.com');
        }
      }
    );
  }
}
