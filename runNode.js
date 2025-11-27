#!/usr/bin/env node

// A script that will run the passed-in script within node, with support for ES6-et-al
// Can be used in the hash-bang script line.

process.on('unhandledRejection', (reason, p) => {
  console.error('Unhandled Rejection at: Promise ', p, ' reason: ', reason);
  throw reason;
});

var path = require('path');
require('@babel/register');
require('core-js/stable');
require('regenerator-runtime/runtime');
var binPath = process.argv[2];
if (!binPath.startsWith('/')) {
  binPath = path.join(process.cwd(), binPath);
}
require(binPath);
