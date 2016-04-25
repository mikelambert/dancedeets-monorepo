import trackjs from 'react-native-trackjs';
import crashlytics_reporter from 'react-native-crashlytics-reporter';

export default function init() {
  trackjs.init({token: '77a8a7079d734df7a94150f8f0d7e16f'});
  crashlytics_reporter.init();
}
