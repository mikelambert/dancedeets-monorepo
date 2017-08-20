/* eslint-disable import/first */
import './common';
import jQuery from 'jquery';

global.$ = global.jQuery = jQuery;

// These depend on a jQuery being implicitly in scope,
// so we need to require them instead of importing them.
require('jquery-backstretch');
/* eslint-enable import/first */

jQuery(document).ready(() => {
  setupHomepage();
});

function setupHomepage() {
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
  if (jQuery(document).width() > 900) {
    images = images.map(x => x.replace('.jpg', '@2x.jpg'));
  }
  jQuery('.fullscreen-static-image').backstretch(images, {
    duration: 8000,
    fade: 1500,
  });
}
