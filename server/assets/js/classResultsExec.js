/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import App from './classResults';

ReactDOM.render(
  <App
    {...window._REACT_PROPS}
  />,
  document.getElementById(window._REACT_ID)
);
