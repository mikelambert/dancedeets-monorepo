/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import querystring from 'querystring';

function ajaxFetch(url: string, body: Object) {
  const result = fetch('/events/rsvp_ajax', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    },
    body: querystring.stringify(body),
  });
  return result;
}

export default ajaxFetch;
