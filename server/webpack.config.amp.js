/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

const uncssWebpackGenerator = require('./uncssWebpackGenerator');

module.exports = uncssWebpackGenerator('amp', ['amp/generated/*-amp.html']);
