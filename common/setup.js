/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import AppContainer from './containers/AppContainer';
//var FacebookSDK = require('FacebookSDK');
import React from 'React';
import {Provider} from 'react-redux';
import configureStore from './store/configureStore';
import {serverURL} from './env';

function setup(): React.Component {
  console.disableYellowBox = true;

  class Root extends React.Component {
    constructor() {
      super();
      this.state = {
        isLoading: true,
        store: configureStore(() => this.setState({isLoading: false})),
      };
    }
    render() {
      if (this.state.isLoading) {
        return null;
      }
      return (
        <Provider store={this.state.store}>
          <AppContainer />
        </Provider>
      );
    }
  }

  return Root;
}

global.LOG = (...args) => {
  console.log('/------------------------------\\');
  console.log(...args);
  console.log('\\------------------------------/');
  return args[args.length - 1];
};

module.exports = setup;
