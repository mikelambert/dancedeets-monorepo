/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { addLocaleData, IntlProvider } from 'react-intl';
import moment from 'moment';
import 'moment/locale/fr';
import 'moment/locale/ja';
import 'moment/locale/zh-tw';
import fr from './messages/fr.json';
import ja from './messages/ja.json';
import zh from './messages/zh.json';

export const defaultLocale = 'en';

// TODO: Keep in sync with mobile/js/intlPolyfill.js
const messages = {
  en: null, // use built-ins...but ensure we have an entry so we don't have undefined flow errors
  fr,
  ja,
  'zh-tw': zh,
};

if (!global.Intl) {
  console.error('Tried to load common/js/intl.js prior to the Intl Polyfill');
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

class Internationalize extends React.Component {
  props: {
    currentLocale: string,
    children?: Array<React.Element<*>>,
  };

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
  return (props: Object) =>
    <Internationalize {...props}>
      <Wrapped {...props} />
    </Internationalize>;
}

// currentLocale here is of the form:
// en-US
// fr-FR
// zh-Hant-US
// etc
export function intl(Wrapped: any, currentLocale: string) {
  return (props: Object) =>
    <Internationalize
      currentLocale={currentLocale}
      defaultLocale={defaultLocale}
    >
      <Wrapped {...props} />
    </Internationalize>;
}
