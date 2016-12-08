
import './stackdriver-errors';

require('trackjs');

const $ = require('jquery');

global.$ = global.jQuery = $;

require('jquery.backstretch');
// TODO: Remove this once we are fully live with the React templates for list views
require('jquery-lazyload');

require('jquery.smartbanner');

require('bootstrap');

require('./all-css');

const App = require('./app');

const fbSetup = require('./fb');

const fixStickyTouch = require('./sticky-touch');

const appInstallPromos = require('./app-install-promo');

fbSetup(window.fbPermissions, window.fbAppId, window.baseHostname);

if (window.showSmartBanner) {
  $.smartbanner({
    title: 'DanceDeets',
    author: 'DanceDeets',
    icon: '/images/ic_launcher_dancedeets.png',
  });
}

$(document).ready(() => {
  App.init($);
  fixStickyTouch(window);
  appInstallPromos(window);

  // background-image rotation
  let images = [
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
    images = images.map(x => x.replace('.jpg', '@2x.jpg'));
  }
  $('.fullscreen-static-image').backstretch(images, { duration: 8000, fade: 1500 });

  // animate-on-hover
  $('.animate-on-hover').hover(() => {
    const action = $(this).data('action');
    $(this).addClass(`animated ${action}`);
  });
  $('.animate-on-hover').bind('animationend webkitAnimationEnd oAnimationEnd MSAnimationEnd', () => {
    const action = $(this).data('action');
    $(this).removeClass(`animated ${action}`);
  });

  $('#location_submit').click(() => Boolean($('#location').val()));
});
