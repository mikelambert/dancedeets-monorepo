/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import uncssWebpackGenerator from './uncssWebpackGenerator';

module.exports = uncssWebpackGenerator(
  'full',
  ['amp/generated/*-full.html'],
  // This contains the css to hide modals on initial display (until shown).
  // Unfortunately our source files don't yet contain these modal divs.
  ['.modal']
);
