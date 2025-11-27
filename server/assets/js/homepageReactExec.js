/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import './common';
import renderReact from './renderReact';
import './homepage'; // Side-effect import for jQuery backstretch setup

function render() {
  renderReact(require('./homepageReact').default); // eslint-disable-line global-require
}

render();

if (module.hot) {
  module.hot.accept('./homepageReact', render);
}
