/*
* Template Na  me: Unify - Responsive Bootstrap Template
* Version: 1.9
* Author: @htmlstream
* Website: http://htmlstream.com
*/
import jQuery from 'jquery';

const App = (() => {
  // Header Mega Menu
  function handleMegaMenu() {
    jQuery(document).on('click', '.mega-menu .dropdown-menu', (e) => {
      e.stopPropagation();
    });
  }

  return {
    init() {
      handleMegaMenu();
    },

    // Animate Dropdown
    initAnimateDropdown() {
      function menuMode() {
        jQuery('.dropdown').on('show.bs.dropdown', () => {
          const menu = jQuery(this).find('.dropdown-menu');
          menu.first().stop(true, true).slideDown();
        });
        jQuery('.dropdown').on('hide.bs.dropdown', () => {
          const menu = jQuery(this).find('.dropdown-menu');
          menu.first().stop(true, true).slideUp();
        });
      }

      jQuery(window).resize(() => {
        if (jQuery(window).width() > 768) {
          menuMode();
        }
      });

      if (jQuery(window).width() > 768) {
        menuMode();
      }
    },
  };
})();

module.exports = App;
