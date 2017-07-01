import trackjs from 'react-native-trackjs';
import crashlyticsReporter from 'react-native-fabric-crashlytics';
import { Sentry } from 'react-native-sentry';

export default function init() {
  if (__DEV__) {
    // Don't send exceptions from __DEV__, it's way too noisy!
    // Live reloading and hot reloading in particular lead to tons of noise...
    return;
  }
  Sentry.config(
    'https://56b58e9bc5c44335ab7ef39a1f85d1aa:5d0631b36af0489fab9eae00b9953e4f@sentry.io/106536'
  ).install();

  trackjs.init({
    token: '77a8a7079d734df7a94150f8f0d7e16f',
    application: 'react-native',
  });
  crashlyticsReporter.init();
}
