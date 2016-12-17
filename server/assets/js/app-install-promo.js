import cookie from 'react-cookie';
import $ from 'jquery';

/* center modal */
function initAppPromos(window) {
  function hideAppPromo() {
    cookie.save('ap-closed', '1', { expires: 4 });
  }

  // Only show the promo if it's the second time the user is using the app
  if ($('#app-install')) {
    const appUsed = cookie.load('ap-used');
    if (appUsed) {
      const appPromoClosed = cookie.load('ap-closed');
      if (!appPromoClosed) {
        $('#app-install').modal({});
      }
    }
    cookie.save('ap-used', '1', { expires: 60 });

    $('.onclick-hide-app-promo').on('click', hideAppPromo);
  }
}

module.exports = initAppPromos;
