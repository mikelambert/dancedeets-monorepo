'use strict';

if (window.prod_mode) {
  require('trackjs');
}

var $ = require('jquery');
global.$ = global.jQuery = $;

require('jquery.backstretch');
require('jquery-lazyload');

require('jquery.smartbanner');

require('bootstrap');

require('./all-css');

var App = require('./app');

var fbSetup = require('./fb');

var fixStickyTouch = require('./sticky-touch');

var appInstallPromos = require('./app-install-promo');

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
    'dist/img/background-show-locking.jpg', // slim
    'dist/img/background-class-overhead.jpg', // cricket
    'dist/img/background-club-turntable.jpg', // mario
    'dist/img/background-show-awards.jpg', // slim

    'dist/img/background-class-kids.jpg', // mario
    'dist/img/background-show-pose.jpg', // slim
    'dist/img/background-club-smoke-cypher.jpg', // mario
    'dist/img/background-class-rocking.jpg', // mario
    'dist/img/background-show-dj.jpg', // slim
//    'dist/img/background-club-headspin.jpg',
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
