/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import 'babel-polyfill';
import * as React from 'react';
import ReactDOM from 'react-dom';
import { AppContainer } from 'react-hot-loader';

export default function(
  Component: Class<React.Component<*, *>>,
  props?: Object
) {
  ReactDOM.hydrate(
    <AppContainer>
      <Component {...window._REACT_PROPS} {...props} />
    </AppContainer>,
    document.getElementById(window._REACT_ID)
  );
}
