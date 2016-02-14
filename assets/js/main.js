'use strict';

if (window.prod_mode) {
  require('trackjs');
}

var $ = require('jquery');
global.$ = global.jQuery = $;

require('jquery.backstretch');

require('jquery.smartbanner');
require('../../node_modules/jquery.smartbanner/jquery.smartbanner.css');

require('bootstrap');
require('../css/bootstrap-custom.scss');

require('../../node_modules/font-awesome/css/font-awesome.css');
require('../../node_modules/animate.css/animate.css');

require('../css/fonts.scss');
require('../css/dancedeets.scss');
require('../css/social-hovers.scss');
require('../css/header.scss');
require('../css/footer.scss');
require('../css/custom.scss');
require('../../css/dancedeets.css');

var App = require('./app');

var fbSetup = require('./fb');

var fixStickyTouch = require('./sticky-touch');

var appInstallPromos = require('./app-install-promo');

// From old site: jquery.cookie@1.4.1,momentjs@2.10.6,jquery.lazyload@1.9.3

fbSetup(window, window.fbPermissions, window.fbAppId, window.baseHostname);

if (window.showSmartBanner) {
  $.smartbanner({
    title: 'DanceDeets',
    author: 'DanceDeets',
    icon: '/images/ic_launcher_dancedeets.png',
  });
}

$(document).ready(function() {
  App.init($);
  fixStickyTouch(window);
  appInstallPromos(window);

  // background-image rotation
  var images = [
    'dist/img/background-show-locking.jpg',
    'dist/img/background-class-overhead.jpg',
    'dist/img/background-club-turntable.jpg',
    'dist/img/background-show-awards.jpg',

    'dist/img/background-class-kids.jpg',
    'dist/img/background-show-pose.jpg',
    'dist/img/background-club-smoke-cypher.jpg',
    'dist/img/background-class-rocking.jpg',
    'dist/img/background-show-dj.jpg',
    'dist/img/background-club-headspin.jpg',
  ];
  if ($(document).width() > 900) {
    images = images.map(function(x) {
      return x.replace('.jpg', '@2x.jpg');
    });
  }
  $('.fullscreen-static-image').backstretch(images, {duration: 8000, fade: 1500});

  // animate-on-hover
  $('.animate-on-hover').hover(function() {
    $(this).addClass('animated ' + $(this).data('action'));
  });
  $('.animate-on-hover').bind('animationend webkitAnimationEnd oAnimationEnd MSAnimationEnd', function() {
    $(this).removeClass('animated ' + $(this).data('action'));
  });
});
