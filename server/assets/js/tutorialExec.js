/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import './common';
import renderReact from './renderReact';

function render() {
  const hashLocation = window.location.hash.replace(/^#\/?|\/$/g, '');
  const props = { hashLocation };
  renderReact(require('./tutorial').default, props); // eslint-disable-line global-require
}

render();

window.addEventListener('hashchange', render, false);

if (module.hot) {
  module.hot.accept('./tutorial', render);
}
