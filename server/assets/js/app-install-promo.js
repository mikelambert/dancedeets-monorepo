/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import cookie from 'react-cookie';
import jQuery from 'jquery';
import { queryOn } from './dom';

function hideAppPromo() {
  cookie.save('ap-closed', '1', { expires: 4 });
}

/* center modal */
function initAppPromos() {
  // Only show the promo if it's the second time the user is using the app
  if (document.getElementById('app-install')) {
    const appUsed = cookie.load('ap-used');
    if (appUsed) {
      const appPromoClosed = cookie.load('ap-closed');
      if (!appPromoClosed) {
        jQuery('#app-install').modal({});
      }
    }
    cookie.save('ap-used', '1', { expires: 60 });

    queryOn('.onclick-hide-app-promo', 'click', hideAppPromo);
  }
}

module.exports = initAppPromos;
