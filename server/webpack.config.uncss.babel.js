/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import uncssWebpackGenerator from './uncssWebpackGenerator';

module.exports = uncssWebpackGenerator(
  'full',
  ['amp/generated/*-full.html'],
  ['.modal']
);
