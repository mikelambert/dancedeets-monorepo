/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

/* eslint-disable import/first */
// We need to import the two error handlers first
import Raven from 'raven-js';
import fixStickyTouch from './sticky-touch';

// Then we need to import jQuery and set it up,
// before we important any jquery-dependent libraries.
import jQuery from 'jquery';

global.$ = global.jQuery = jQuery;

// These depend on a jQuery being implicitly in scope,
// so we need to require them instead of importing them.
require('jquery.smartbanner');
require('bootstrap');

// Now let's import the rest normally.
import './all-css';
import './stackdriver-errors';
import { fbSetup } from './fb';
import appInstallPromos from './app-install-promo';
import { queryOn } from './dom';
/* eslint-enable import/first */

Raven
  .config('https://f966ae7e625249f8a36d42e8b521dc2f@sentry.io/159133', {
    environmnent: window.prodMode ? 'prod' : 'dev',
  })
  .install();
window.addEventListener('unhandledrejection', event => Raven.captureException(event.reason));

fbSetup(window.fbPermissions, window.fbAppId, window.baseHostname);

if (window.showSmartBanner) {
  jQuery.smartbanner({
    title: 'DanceDeets',
    author: 'DanceDeets',
    icon: '/images/ic_launcher_dancedeets.png',
  });
}

jQuery(document).ready(() => {
  queryOn('.mega-menu .dropdown-menu', 'click', (e) => {
    e.stopPropagation();
  });

  fixStickyTouch();
  appInstallPromos();

  jQuery('#location_submit').click(() => Boolean(jQuery('#location').val()));
});
