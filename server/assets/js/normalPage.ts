/**
 * Copyright 2016 DanceDeets.
 */

import jQuery from 'jquery';
import './common';

declare global {
  // eslint-disable-next-line no-var
  var $: typeof jQuery;
  // eslint-disable-next-line no-var
  var jQuery: typeof jQuery;
}

global.$ = jQuery;
global.jQuery = jQuery;
