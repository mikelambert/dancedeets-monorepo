/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

/* eslint no-unused-vars:0 */
// This is for hot module reloading calls:
// module.hot.accept(path, fn);
declare var module: {
  hot: {
    accept: (path: string, fn: () => void) => void;
  };
};
