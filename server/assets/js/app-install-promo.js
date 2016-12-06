const $ = require('jquery');

/* center modal */
function initAppPromos(window) {
  function hideAppPromo() {
    $.cookie('ap-closed', '1', { expires: 4 });
  }

  // Only show the promo if it's the second time the user is using the app
  if ($('#app-install')) {
    const appUsed = $.cookie('ap-used');
    if (appUsed) {
      const appPromoClosed = $.cookie('ap-closed');
      if (!appPromoClosed) {
        $('#app-install').modal({});
      }
    }
    $.cookie('ap-used', '1', { expires: 60 });

    $('.onclick-hide-app-promo').on('click', hideAppPromo);
  }
}

module.exports = initAppPromos;
