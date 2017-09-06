/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import uncssWebpackGenerator from './uncssWebpackGenerator';

module.exports = uncssWebpackGenerator('eventAmp', [
  'amp/generated/*-amp.html',
]);
