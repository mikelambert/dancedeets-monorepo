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
  renderReact(require('./tutorialCategory').default, props); // eslint-disable-line global-require
}

render();

// We don't need to listen, since we update the state internally and reflect it in the hash.
// Changes to the hash itself shouldn't be triggering anything ourselves.
// window.addEventListener('hashchange', render, false);

if (module.hot) {
  module.hot.accept('./tutorialCategory', render);
}
