/**
 * Copyright 2016 DanceDeets.
 */

import './common';
import renderReact from './renderReact';

declare const module: {
  hot?: {
    accept(path: string, callback: () => void): void;
  };
};

function render(): void {
  const hashLocation = window.location.hash.replace(/^#\/?|\/$/g, '');
  const props = { hashLocation };
  // eslint-disable-next-line global-require, @typescript-eslint/no-var-requires
  renderReact(require('./tutorialCategory').default, props);
}

render();

// We don't need to listen, since we update the state internally and reflect it in the hash.
// Changes to the hash itself shouldn't be triggering anything ourselves.
// window.addEventListener('hashchange', render, false);

if (module.hot) {
  module.hot.accept('./tutorialCategory', render);
}
