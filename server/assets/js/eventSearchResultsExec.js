/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import EventSearchResults from './eventSearchResults';

ReactDOM.render(
  <EventSearchResults
    {...window._REACT_PROPS}
  />,
  document.getElementById(window._REACT_ID)
);
