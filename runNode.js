#!/usr/local/bin/node

process.on('unhandledRejection', (reason, p) => {
  console.error('Unhandled Rejection at: Promise ', p, ' reason: ', reason);
  throw reason;
});

var path = require('path');
require('babel-core/register');
require('babel-polyfill');
require(path.join(process.cwd(), process.argv[2]));
