import trackjs from 'react-native-trackjs';
import crashlytics_reporter from 'react-native-fabric-crashlytics';

export default function init() {
  if (__DEV__) {
    // Don't send exceptions from __DEV__, it's way too noisy!
    // Live reloading and hot reloading in particular lead to tons of noise...
    return;
  }
  trackjs.init({
    token: '77a8a7079d734df7a94150f8f0d7e16f',
    application: 'react-native',
  });
  crashlytics_reporter.init();
}
