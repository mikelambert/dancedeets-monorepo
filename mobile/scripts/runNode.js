#!/usr/local/bin/node

process.on('unhandledRejection', (reason, p) => {
  console.error('Unhandled Rejection at: Promise ', p, ' reason: ', reason);
});

require('babel-core/register');
require('babel-polyfill');
require(process.argv[2]);
