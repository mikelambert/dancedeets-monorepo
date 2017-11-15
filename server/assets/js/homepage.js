/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

/* eslint-disable import/first */
import { cdnBaseUrl } from 'dancedeets-common/js/util/url';
import './common';
import jQuery from 'jquery';

global.$ = jQuery;
global.jQuery = jQuery;

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
    `${cdnBaseUrl}/img/background-show-locking.jpg`, // slim
    `${cdnBaseUrl}/img/background-class-overhead.jpg`, // cricket
    `${cdnBaseUrl}/img/background-club-turntable.jpg`, // mario
    `${cdnBaseUrl}/img/background-show-awards.jpg`, // slim

    `${cdnBaseUrl}/img/background-class-kids.jpg`, // mario
    `${cdnBaseUrl}/img/background-show-pose.jpg`, // slim
    `${cdnBaseUrl}/img/background-club-smoke-cypher.jpg`, // mario
    `${cdnBaseUrl}/img/background-class-rocking.jpg`, // mario
    `${cdnBaseUrl}/img/background-show-dj.jpg`, // slim
    //    `${cdnBaseUrl}/img/background-club-headspin.jpg`,
  ];
  if (jQuery(document).width() > 900) {
    images = images.map(x => x.replace('.jpg', '@2x.jpg'));
  }
  jQuery('.fullscreen-static-image').backstretch(images, {
    duration: 8000,
    fade: 1500,
  });
}
