/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { Platform } from 'react-native';
import { Provider } from 'react-redux';
import Mixpanel from 'react-native-mixpanel';
import ProcessInfo from 'react-native-processinfo';
import { intl } from 'dancedeets-common/js/intl';
import App from './app';
import configureStore from '../store/configureStore';
import ScreenshotSlideshow from '../ScreenshotSlideshow';
// Initialize firestack
import firestack from '../firestack';
import { getCurrentLocale } from '../locale';

export default function setup() {
  console.disableYellowBox = true;

  class Root extends React.Component {
    constructor() {
      super();
      this.state = {
        store: configureStore(),
      };
    }

    state: {
      store: any,
    };

    render() {
      let app = <App />;
      if (Platform.OS === 'ios' && ProcessInfo.environment.UITest) {
        app = <ScreenshotSlideshow>{app}</ScreenshotSlideshow>;
      }
      return (
        <Provider store={this.state.store}>
          {app}
        </Provider>
      );
    }
  }

  return intl(Root, getCurrentLocale());
}

global.LOG = (...args) => {
  console.log('/------------------------------\\');
  console.log(...args);
  console.log('\\------------------------------/');
  return args[args.length - 1];
};
