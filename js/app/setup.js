/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import App from './app';
import React from 'react';
import { Platform } from 'react-native';
import { Provider } from 'react-redux';
import configureStore from '../store/configureStore';
import Mixpanel from 'react-native-mixpanel';
import ScreenshotSlideshow from '../ScreenshotSlideshow';
import intl from '../intl';
import ProcessInfo from 'react-native-processinfo';
import { setup as setupNotifications } from '../notifications/setup';

export default function setup(): Class<Object> {
  console.disableYellowBox = true;

  if (__DEV__) {
    Mixpanel.sharedInstanceWithToken('668941ad91e251d2ae9408b1ea80f67b');
  } else {
    Mixpanel.sharedInstanceWithToken('f5d9d18ed1bbe3b190f9c7c7388df243');
  }

  class Root extends React.Component {
    state: {
      isLoading: boolean,
      store: any,
    };

    constructor() {
      super();
      this.state = {
        isLoading: true,
        store: configureStore(() => this.setState({isLoading: false})),
      };
      setupNotifications(this.state.store);
    }

    render() {
      if (this.state.isLoading) {
        return null;
      }
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

  return intl(Root);
}

global.LOG = (...args) => {
  console.log('/------------------------------\\');
  console.log(...args);
  console.log('\\------------------------------/');
  return args[args.length - 1];
};
