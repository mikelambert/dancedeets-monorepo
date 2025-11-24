/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import 'babel-polyfill';
import * as React from 'react';
import ReactDOM from 'react-dom';
import { AppContainer } from 'react-hot-loader';

// Would like to define it as Class<React.Component<*, *>>, but doesn't work with the functions required by import
export default function(Component: any, props?: Object) {
  ReactDOM.render(
    <AppContainer>
      <Component {...window._REACT_PROPS} {...props} />
    </AppContainer>,
    document.getElementById(window._REACT_ID)
  );
}
