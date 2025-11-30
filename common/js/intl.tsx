/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { IntlProvider, createIntl, createIntlCache, IntlShape } from 'react-intl';
import areIntlLocalesSupported from 'intl-locales-supported';
import moment from 'moment';
import 'moment/locale/fr';
import 'moment/locale/ja';
import 'moment/locale/zh-tw';
import fr from './messages/fr.json';
import ja from './messages/ja.json';
import zh from './messages/zh.json';

export const defaultLocale = 'en';

type MessageRecord = Record<string, string> | null;

const messages: Record<string, MessageRecord> = {
  en: null, // use built-ins...but ensure we have an entry so we don't have undefined errors
  fr: fr as MessageRecord,
  ja: ja as MessageRecord,
  'zh-tw': zh as MessageRecord,
};

declare const global: {
  Intl?: typeof Intl & {
    __addLocaleData?: () => void;
  };
  IntlPolyfill?: typeof Intl;
};

// Skip the Intl polyfill if we are building for the browser
if (!process.env.BROWSER) {
  /* eslint-disable global-require, import/no-extraneous-dependencies, @typescript-eslint/no-var-requires */
  // https://github.com/yahoo/intl-locales-supported#usage
  if (global.Intl) {
    // Determine if the built-in `Intl` has the locale data we need.
    if (!areIntlLocalesSupported(Object.keys(messages))) {
      // `Intl` exists, but it doesn't have the data we need, so load the
      // polyfill and replace the constructors we need with the polyfill's.
      require('intl');
      if (global.IntlPolyfill) {
        (global.Intl as typeof Intl).NumberFormat = global.IntlPolyfill.NumberFormat;
        (global.Intl as typeof Intl).DateTimeFormat = global.IntlPolyfill.DateTimeFormat;
      }
    }
  } else {
    // No `Intl`, so use and load the polyfill.
    (global as Record<string, unknown>).Intl = require('intl');
  }

  // Only load these if we're using the polyfill (that exposes this function)
  if (global.Intl?.__addLocaleData) {
    // These have number formatting, useful for NumberFormat and DateTimeFormat
    require('intl/locale-data/jsonp/en');
    require('intl/locale-data/jsonp/fr');
    require('intl/locale-data/jsonp/ja');
    require('intl/locale-data/jsonp/zh');
  }
  /* eslint-enable global-require, import/no-extraneous-dependencies, @typescript-eslint/no-var-requires */
}

// Note: addLocaleData was removed in react-intl v3+.
// In react-intl v6, locale data is loaded automatically from the browser's Intl API
// or from @formatjs/intl-* polyfill packages if needed.

interface IntlProviderArgs {
  defaultLocale: string;
  key: string;
  locale: string;
  messages: MessageRecord;
}

function intlProviderArgs(currentLocale: string): IntlProviderArgs {
  // Our Locale.constants().localeIdentifier returns zh-Hant_US (converted to zh-Hant-US).
  // But moment locales are zh-tw (traditional) and zh-cn (simplified).
  // So manually convert the currentLocale to the 'zh-tw' moment needs:
  let locale = (currentLocale || defaultLocale).toLowerCase();
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

// Cache for createIntl to improve performance
const intlCache = createIntlCache();

export function constructIntl(currentLocale: string): IntlShape {
  const args = intlProviderArgs(currentLocale);
  // Use createIntl from react-intl v6 instead of IntlProvider.getChildContext()
  return createIntl(
    {
      locale: args.locale,
      messages: args.messages || {},
      defaultLocale: args.defaultLocale,
    },
    intlCache
  );
}

interface InternationalizeProps {
  currentLocale: string;
  children?: React.ReactNode;
}

function Internationalize(props: InternationalizeProps): React.ReactElement {
  const args = intlProviderArgs(props.currentLocale);
  return (
    <IntlProvider
      locale={args.locale}
      messages={args.messages || {}}
      defaultLocale={args.defaultLocale}
      key={args.key}
    >
      <>{props.children}</>
    </IntlProvider>
  );
}

// props.currentLocale here is of the form:
// en-US
// fr-FR
// zh-TW
// etc
// The wrapped component receives all props including currentLocale,
// but may choose to ignore it since Internationalize uses it for the IntlProvider.
export function intlWeb<P extends object>(
  Wrapped: React.ComponentType<P>
): React.FC<Omit<P, 'currentLocale'> & { currentLocale: string }> {
  const IntlWrapped: React.FC<Omit<P, 'currentLocale'> & { currentLocale: string }> = (props) => (
    <Internationalize currentLocale={props.currentLocale}>
      <Wrapped {...(props as unknown as P)} />
    </Internationalize>
  );
  return IntlWrapped;
}

// currentLocale here is of the form:
// en-US
// fr-FR
// zh-Hant-US
// etc
export function intl<P extends object>(
  Wrapped: React.ComponentType<P>,
  currentLocale: string
): React.FC<P> {
  return (props: P) => (
    <Internationalize currentLocale={currentLocale}>
      <Wrapped {...props} />
    </Internationalize>
  );
}
