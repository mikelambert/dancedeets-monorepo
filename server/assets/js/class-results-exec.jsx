/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import ReactDOM from 'react-dom';
import App from './class-results';

ReactDOM.render(
  <App
    imagePath={window.imagePath}
    location={window.searchLocation}
    classes={window.classes}
  />,
  document.getElementById('app')
);
