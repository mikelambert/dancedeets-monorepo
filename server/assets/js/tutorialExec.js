/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import './common';
import renderReact from './renderReact';

function render() {
  const locationComponents = window.location.hash.replace(/^#\/?|\/$/g, '').split('/');
  const props = { locationComponents };
  renderReact(require('./tutorial').default, props); // eslint-disable-line global-require
}

render();

window.addEventListener('hashchange', render, false);

if (module.hot) {
  module.hot.accept('./tutorial', render);
}
