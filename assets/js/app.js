/*
* Template Na  me: Unify - Responsive Bootstrap Template
* Version: 1.9
* Author: @htmlstream
* Website: http://htmlstream.com
*/

var App = (function(jQuery) {
  var $ = jQuery;
  // Fixed Header
  function handleHeader() {
    jQuery(window).scroll(function() {
      if (jQuery(window).scrollTop() > 100) {
        jQuery('.header-fixed .header-sticky').addClass('header-fixed-shrink');
      } else {
        jQuery('.header-fixed .header-sticky').removeClass('header-fixed-shrink');
      }
    });
  }

  // Header Mega Menu
  function handleMegaMenu() {
    jQuery(document).on('click', '.mega-menu .dropdown-menu', function(e) {
      e.stopPropagation();
    });
  }

  // Equal Height Columns
  function handleEqualHeightColumns() {
    var equalHeightColumns = function() {
      $('.equal-height-columns').each(function() {
        var heights = [];
        $('.equal-height-column', this).each(function() {
          $(this).removeAttr('style');
          // write column's heights to the array
          heights.push($(this).height());
        });
        // find and set max
        $('.equal-height-column', this).height(Math.max.apply(Math, heights));
      });
    };

    equalHeightColumns();
    $(window).resize(function() {
      equalHeightColumns();
    });
    $(window).load(function() {
      equalHeightColumns('img.equal-height-column');
    });
  }

  // Full Screen
  var handleFullscreen = function() {
    var WindowHeight = $(window).height();
    var HeaderHeight;

    if ($(document.body).hasClass('promo-padding-top')) {
      HeaderHeight = $('.header').height();
    } else {
      HeaderHeight = 0;
    }

    $('.fullheight').css('height', WindowHeight - HeaderHeight);

    $(window).resize(function() {
      var WindowHeight = $(window).height();
      $('.fullheight').css('height', WindowHeight - HeaderHeight);
    });
  };

  // Align Middle
  var handleValignMiddle = function() {
    $('.valign__middle').each(function() {
      $(this).css('padding-top', $(this).parent().height() / 2 - $(this).height() / 2);
    });
    $(window).resize(function() {
      $('.valign__middle').each(function() {
        $(this).css('padding-top', $(this).parent().height() / 2 - $(this).height() / 2);
      });
    });
  };

  // Bootstrap Tooltips and Popovers
  function handleBootstrap() {
    /* Bootstrap Carousel */
    jQuery('.carousel').carousel({
      interval: 15000,
      pause: 'hover',
    });

    /* Tooltips */
    jQuery('.tooltips').tooltip();
    jQuery('.tooltips-show').tooltip('show');
    jQuery('.tooltips-hide').tooltip('hide');
    jQuery('.tooltips-toggle').tooltip('toggle');
    jQuery('.tooltips-destroy').tooltip('destroy');

    /* Popovers */
    jQuery('.popovers').popover();
    jQuery('.popovers-show').popover('show');
    jQuery('.popovers-hide').popover('hide');
    jQuery('.popovers-toggle').popover('toggle');
    jQuery('.popovers-destroy').popover('destroy');
  }

  return {
    init: function() {
      handleBootstrap();
      handleHeader();
      handleMegaMenu();
      handleFullscreen();
      handleValignMiddle();
      handleEqualHeightColumns();
    },

    // Parallax Backgrounds
    initParallaxBg: function() {
      jQuery(window).load(function() {
        jQuery('.parallaxBg').parallax('50%', 0.2);
        jQuery('.parallaxBg1').parallax('50%', 0.4);
      });
    },

    // Animate Dropdown
    initAnimateDropdown: function() {
      function menuMode() {
        jQuery('.dropdown').on('show.bs.dropdown', function() {
          jQuery(this).find('.dropdown-menu').first().stop(true, true).slideDown();
        });
        jQuery('.dropdown').on('hide.bs.dropdown', function() {
          jQuery(this).find('.dropdown-menu').first().stop(true, true).slideUp();
        });
      }

      jQuery(window).resize(function() {
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
