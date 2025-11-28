/**
 * Copyright 2016 DanceDeets.
 */

import cookie from 'react-cookie';
import jQuery from 'jquery';
import moment from 'moment';
import { queryOn } from './dom';

interface JQueryWithModal extends JQuery {
  modal(options?: object): void;
}

function hideAppPromo(): void {
  cookie.save('ap-closed', '1', {
    expires: moment()
      .add(4, 'days')
      .toDate(),
    path: '/',
  });
}

/* center modal */
function initAppPromos(): void {
  // Only show the promo if it's the second time the user is using the app
  if (document.getElementById('app-install')) {
    const appUsed = cookie.load('ap-used');
    if (appUsed) {
      const appPromoClosed = cookie.load('ap-closed');
      if (!appPromoClosed) {
        (jQuery('#app-install') as JQueryWithModal).modal({});
      }
    }
    cookie.save('ap-used', '1', {
      expires: moment()
        .add(60, 'days')
        .toDate(),
      path: '/',
    });

    queryOn('.onclick-hide-app-promo', 'click', hideAppPromo);
  }
}

export default initAppPromos;
