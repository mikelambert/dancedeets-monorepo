/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import ReactDOM from 'react-dom';
import EventPage from './event';

ReactDOM.render(
  <EventPage
    {...window._REACT_PROPS}
  />,
  document.getElementById(window._REACT_ID)
);
