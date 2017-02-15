/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import {
  Linking,
  Platform,
} from 'react-native';
import { performRequest } from '../api/fb';

export async function openUserId(userId: String) {
  let adminUrl = null;
  // On Android, just send them to the URL and let the native URL intecerpetor send it to FB.
  if (Platform.OS === 'ios' && await Linking.canOpenURL('fb://')) {
    // We don't really need to pass fields=, but the FB SDK complains if we don't
    const metadata = await performRequest('GET', userId, { metadata: '1', fields: '' });
    const idType = metadata.metadata.type;
    if (idType === 'user') {
      // This should work, but doesn't...
      // adminUrl = 'fb://profile/' + userId;
      // So let's send them to the URL directly:
      adminUrl = `https://www.facebook.com/app_scoped_user_id/${userId}`;
    } else if (idType === 'page') {
      adminUrl = `fb://page/?id=${userId}`;
    } else {
      adminUrl = `https://www.facebook.com/${userId}`;
    }
    // Every event lists all members of the event who created it
    // Group events only list members (not the group, which is in a different field)
    // Page events list the members and the page id, too
  } else {
    adminUrl = `https://www.facebook.com/${userId}`;
  }
  try {
    Linking.openURL(adminUrl);
  } catch (err) {
    console.error('Error opening FB admin page:', adminUrl, ', with Error:', err);
  }
}
