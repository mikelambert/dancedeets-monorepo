/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import type { ReactClass } from 'react/lib/ReactClass';
import { AppContainer } from 'react-hot-loader';

export default function (Component: ReactClass) {
  ReactDOM.render(
    <AppContainer>
      <Component
        {...window._REACT_PROPS}
      />
    </AppContainer>,
    document.getElementById(window._REACT_ID)
  );
}

