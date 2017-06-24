#!/usr/bin/env node

// A script that will run the passed-in script within node, with support for ES6-et-al
// Can be used in the hash-bang script line.

process.on('unhandledRejection', (reason, p) => {
  console.error('Unhandled Rejection at: Promise ', p, ' reason: ', reason);
  throw reason;
});

var path = require('path');
require('babel-core/register');
require('babel-polyfill');
require(path.join(process.cwd(), process.argv[2]));
