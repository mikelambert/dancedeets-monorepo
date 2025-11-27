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
  // eslint-disable-next-line global-require, @typescript-eslint/no-var-requires
  renderReact(require('./brackets').default);
}

render();

if (module.hot) {
  module.hot.accept('./brackets', render);
}
