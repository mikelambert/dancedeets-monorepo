/**
 * Copyright 2016 DanceDeets.
 */

import { Alert, Linking, NativeModules, Platform } from 'react-native';
import querystring from 'querystring';

const Mailer = NativeModules.RNMail;

interface MailOptions {
  subject: string;
  to: string;
  body: string;
}

async function sendGmail(subject: string, to: string, body: string): Promise<boolean> {
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

export default async function sendMail(props: MailOptions): Promise<void> {
  const { subject, to, body } = props;
  if (!await sendGmail(subject, to, body)) {
    Mailer.mail(
      {
        subject,
        recipients: [to],
        body,
      },
      (error: Error | null, event: string) => {
        if (error) {
          Alert.alert('Error', 'Please email us at feedback@dancedeets.com');
        }
      }
    );
  }
}
