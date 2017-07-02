import areIntlLocalesSupported from 'intl-locales-supported';

// TODO: Keep in sync with common/js/intl.js
const supportedLocales = ['en', 'fr', 'ja', 'zh-tw'];

/* eslint-disable global-require, import/no-extraneous-dependencies */
// https://github.com/yahoo/intl-locales-supported#usage
if (global.Intl) {
  // Determine if the built-in `Intl` has the locale data we need.
  if (!areIntlLocalesSupported(supportedLocales)) {
    // `Intl` exists, but it doesn't have the data we need, so load the
    // polyfill and replace the constructors we need with the polyfill's.
    require('intl');
    global.Intl.NumberFormat = global.IntlPolyfill.NumberFormat; // eslint-disable-line no-undef
    global.Intl.DateTimeFormat = global.IntlPolyfill.DateTimeFormat; // eslint-disable-line no-undef
  }
} else {
  // No `Intl`, so use and load the polyfill.
  global.Intl = require('intl');
}

// Only load these if we're using the polyfill (that exposes this function)
if (global.Intl.__addLocaleData) {
  // These have number formtting, useful for NumberFormat and DateTimeFormat
  require('intl/locale-data/jsonp/en');
  require('intl/locale-data/jsonp/fr');
  require('intl/locale-data/jsonp/ja');
  require('intl/locale-data/jsonp/zh');
}
/* eslint-enable global-require, import/no-extraneous-dependencies */

// Now having loaded the above, let's load the common intl.js stuff
require('dancedeets-common/js/intl');
