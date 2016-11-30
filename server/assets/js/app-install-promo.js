const $ = require('jquery');

/* center modal */
function initAppPromos(window) {
  function centerModals() {
    $('.modal').each((/* i */) => {
      const clone = $(this).clone().css('display', 'block').appendTo('body');
      let top = Math.round((clone.height() - clone.find('.modal-content').height()) / 2);
      top = top > 0 ? top : 0;
      clone.remove();
      $(this).find('.modal-content').css('margin-top', top);
    });
  }

  function hideAppPromo() {
    $.cookie('ap-closed', '1', { expires: 4 });
  }

  // Only show the promo if it's the second time the user is using the app
  if ($('#app-install')) {
    const appUsed = $.cookie('ap-used');
    if (appUsed) {
      $('.modal').on('show.bs.modal', centerModals);
      $(window).on('resize', centerModals);

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
