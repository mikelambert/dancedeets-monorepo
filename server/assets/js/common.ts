/**
 * Copyright 2016 DanceDeets.
 */

/// <reference path="../../types/window.d.ts" />

/* eslint-disable import/first */
// We need to import the two error handlers first
import Raven from 'raven-js';
import fixStickyTouch from './sticky-touch';
import 'console-polyfill';

// Then we need to import jQuery and set it up,
// before we important any jquery-dependent libraries.
import jQuery from 'jquery';

interface JQueryWithSmartBanner {
  smartbanner(options: { title: string; author: string; icon: string }): void;
}

(globalThis as unknown as { $: typeof jQuery }).$ = jQuery;
(globalThis as unknown as { jQuery: typeof jQuery }).jQuery = jQuery;

// These depend on a jQuery being implicitly in scope,
// so we need to require them instead of importing them.
require('jquery.smartbanner');

// Used for collapsing alert message boxes with data-dismiss
require('bootstrap/js/alert');
// Called via jquery(elem).modal();
require('bootstrap/js/modal');
// Used for the top nav menus with data-toggle
require('bootstrap/js/collapse');
require('bootstrap/js/dropdown');
// Used by above plugins, possibly
require('bootstrap/js/transition');

import { cdnBaseUrl } from 'dancedeets-common/js/util/url';

// Now let's import the rest normally.
import './all-css';
// Disable this for now, since we don't need the 60KB, and Raven/Sentry serves us fine
// import './stackdriver-errors';
import { fbSetup } from './fb';
import appInstallPromos from './app-install-promo';
/* eslint-enable import/first */

if (window.prodMode) {
  Raven.config('https://f966ae7e625249f8a36d42e8b521dc2f@sentry.io/159133', {
    environment: window.prodMode ? 'prod' : 'dev',
  }).install();
  window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) =>
    Raven.captureException(event.reason)
  );
}

fbSetup(window.fbPermissions || '', window.fbAppId || '', window.baseHostname || '');

if (window.showSmartBanner) {
  (jQuery as unknown as JQueryWithSmartBanner).smartbanner({
    title: 'DanceDeets',
    author: 'DanceDeets',
    icon: `${cdnBaseUrl}/img/ic_launcher_dancedeets.png`,
  });
}

jQuery(document).ready(() => {
  fixStickyTouch();
  appInstallPromos();
});
