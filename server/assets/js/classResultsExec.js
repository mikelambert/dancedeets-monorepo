/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import renderReact from './renderReact';

function render() {
  renderReact(require('./classResults').default); // eslint-disable-line global-require
}

render();

if (module.hot) {
  module.hot.accept('./classResults', render);
}
