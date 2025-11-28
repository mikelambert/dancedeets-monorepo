/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { Platform } from 'react-native';
import { Provider } from 'react-redux';
import Mixpanel from 'react-native-mixpanel';
import ProcessInfo from 'react-native-processinfo';
import backAndroid from 'react-native-back-android';
import { intl } from 'dancedeets-common/js/intl';
import App from './app';
import configureStore from '../store/configureStore';
import ScreenshotSlideshow from '../ScreenshotSlideshow';
import { getCurrentLocale } from '../locale';
import { Store } from 'redux';

interface State {
  store: Store;
}

export default function setup() {
  console.disableYellowBox = true;

  class Root extends React.Component<{}, State> {
    constructor(props: {}) {
      super(props);
      this.state = {
        store: configureStore(),
      };
    }

    render() {
      let app = <App />;
      if (Platform.OS === 'ios' && ProcessInfo.environment.UITest) {
        app = <ScreenshotSlideshow>{app}</ScreenshotSlideshow>;
      }
      return <Provider store={this.state.store}>{app}</Provider>;
    }
  }

  return backAndroid(intl(Root, getCurrentLocale()));
}

(global as any).LOG = (...args: any[]) => {
  console.log('/------------------------------\\');
  console.log(...args);
  console.log('\\------------------------------/');
  return args[args.length - 1];
};
