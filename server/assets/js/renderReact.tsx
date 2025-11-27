/**
 * Copyright 2016 DanceDeets.
 */

import 'core-js/stable';
import 'regenerator-runtime/runtime';
import * as React from 'react';
import ReactDOM from 'react-dom';
import { AppContainer } from 'react-hot-loader';

export default function renderReact(
  Component: React.ComponentType<Record<string, unknown>>,
  props?: Record<string, unknown>
): void {
  ReactDOM.render(
    <AppContainer>
      <Component {...window._REACT_PROPS} {...props} />
    </AppContainer>,
    document.getElementById(window._REACT_ID)
  );
}
