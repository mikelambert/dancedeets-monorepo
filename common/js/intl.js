/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { addLocaleData, IntlProvider } from 'react-intl';
import areIntlLocalesSupported from 'intl-locales-supported';
import moment from 'moment';
import 'moment/locale/fr';
import 'moment/locale/ja';
import 'moment/locale/zh-tw';
import fr from './messages/fr.json';
import ja from './messages/ja.json';
import zh from './messages/zh.json';

export const defaultLocale = 'en';

const messages = {
  en: null, // use built-ins...but ensure we have an entry so we don't have undefined flow errors
  fr,
  ja,
  'zh-tw': zh,
};

// Skip the Intl polyfill if we are building for the browser
if (!process.env.BROWSER) {
  /* eslint-disable global-require, import/no-extraneous-dependencies */
  // https://github.com/yahoo/intl-locales-supported#usage
  if (global.Intl) {
    // Determine if the built-in `Intl` has the locale data we need.
    if (!areIntlLocalesSupported(Object.keys(messages))) {
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
}

// These has pluralRuleFunction, necessary for react-intl's use of intl-messageformat
addLocaleData(require('react-intl/locale-data/en'));
addLocaleData(require('react-intl/locale-data/fr'));
addLocaleData(require('react-intl/locale-data/ja'));
addLocaleData(require('react-intl/locale-data/zh'));

function intlProviderArgs(currentLocale) {
  // Our Locale.constants().localeIdentifier returns zh-Hant_US (converted to zh-Hant-US).
  // But moment locales are zh-tw (traditional) and zh-cn (simplified).
  // So manually convert the currentLocale to the 'zh-tw' moment needs:
  let locale = currentLocale.toLowerCase();
  if (locale.includes('zh-hant')) {
    locale = 'zh-tw';
  }

  let finalLocale = locale;
  if (!messages[finalLocale]) {
    finalLocale = locale.split('-')[0];
  }
  if (!messages[finalLocale]) {
    finalLocale = defaultLocale;
  }

  console.log(
    `Configure requested with locale ${currentLocale}, using locale: ${finalLocale}`
  );
  moment.locale(finalLocale);
  return {
    defaultLocale,
    key: finalLocale, // https://github.com/yahoo/react-intl/issues/234
    locale: finalLocale,
    messages: messages[finalLocale],
  };
}
// For unit tests:
// intlProviderArgs('zh-Hant-US').locale == 'zh-tw'
// intlProviderArgs('en-US').locale == 'en'
// intlProviderArgs('fr-FR').locale == 'fr'
// intlProviderArgs('de-XX').locale == 'en' // fallback

export function constructIntl(currentLocale: string) {
  return new IntlProvider(intlProviderArgs(currentLocale), {}).getChildContext()
    .intl;
}

class Internationalize extends React.Component<{
  currentLocale: string,
  children: React.Node,
}> {
  render() {
    return (
      <IntlProvider {...intlProviderArgs(this.props.currentLocale)}>
        {this.props.children}
      </IntlProvider>
    );
  }
}

// props.currentLocale here is of the form:
// en-US
// fr-FR
// zh-TW
// etc
export function intlWeb(Wrapped: any) {
  return (props: Object) => (
    <Internationalize {...props}>
      <Wrapped {...props} />
    </Internationalize>
  );
}

// currentLocale here is of the form:
// en-US
// fr-FR
// zh-Hant-US
// etc
export function intl(Wrapped: any, currentLocale: string) {
  return (props: Object) => (
    <Internationalize
      currentLocale={currentLocale}
      defaultLocale={defaultLocale}
    >
      <Wrapped {...props} />
    </Internationalize>
  );
}
