var argv = require('yargs')
  .option('p', {
    alias: 'port',
    description: 'Specify the server\'s port',
    default: 8090,
  })
  .option('a', {
    alias: 'address',
    description: 'Specify the server\'s address',
    default: '127.0.0.1',
  })
  .help('h').alias('h', 'help')
  .strict()
  .argv;

var fs = require('fs');
var http = require('http');
var express = require('express');
var bodyParser = require('body-parser');
var reactRender = require('react-render');

// Ensure support for loading files that contain ES6+7 & JSX
// Disabled for now, since we cannot use this in a webpack-compiled script
// And unfortunately, the 10K file limit on GAE keeps us from using uncompiled.
// require('babel-core/register');

var ADDRESS = argv.address;
var PORT = argv.port;

var app = express();
var server = new http.Server(app);

app.use(bodyParser.json());

app.get('/', function(req, res) {
  res.end('React render server');
});

app.post('/render', function(req, res) {
  fs.readFile(req.body.path, {encoding: 'utf8'}, function(err, data) {
    if (err) {
      res.json({
        error: {
          type: err.constructor.name,
          message: err.message,
          stack: err.stack,
        },
        markup: null,
      });
    } else {
      req.body.component = eval(data); // eslint-disable-line no-eval
      reactRender(req.body, function(err, markup) {
        if (err) {
          res.json({
            error: {
              type: err.constructor.name,
              message: err.message,
              stack: err.stack,
            },
            markup: null,
          });
        } else {
          res.json({
            error: null,
            markup: markup,
          });
        }
      });
    }
  });
});

server.listen(PORT, ADDRESS, function() {
  console.log('React render server listening at http://' + ADDRESS + ':' + PORT);
});
