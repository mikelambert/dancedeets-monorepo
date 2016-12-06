import fs from 'fs';
import http from 'http';
import express from 'express';
import bodyParser from 'body-parser';
import reactRender from 'react-render';
import yargs from 'yargs';

const argv = yargs
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


// Ensure support for loading files that contain ES6+7 & JSX
// Disabled for now, since we cannot use this in a webpack-compiled script
// And unfortunately, the 10K file limit on GAE keeps us from using uncompiled.
// require('babel-core/register');

const ADDRESS = argv.address;
const PORT = argv.port;

const app = express();
const server = new http.Server(app);

app.use(bodyParser.json());

app.get('/', (req, res) => {
  res.end('React render server');
});

app.post('/render', (req, res) => {
  // We're constructing new objects everytime we readFile,
  // so let's make sure we clear the cache so it doesn't blow up.
  reactRender._components._cache = [];
  fs.readFile(req.body.path, { encoding: 'utf8' }, (err, data) => {
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
      const body = req.body;
      // We list this here, so that it applies for the eval.
      // But we don't list it at the top, because any attempt to inline this code
      // will trigger runtime errors on the compiled JS.
      require('babel-polyfill');
      // Ensure this runs in a try-catch, so the server cannot die on eval()ing code.
      try {
        body.component = eval(data).default; // eslint-disable-line no-eval
      } catch (e) {
        res.json({
          error: {
            type: e.constructor.name,
            message: e.message,
            stack: e.stack,
          },
          markup: null,
        });
        return;
      }
      reactRender(body, (err2, markup) => {
        if (err2) {
          res.json({
            error: {
              type: err2.constructor.name,
              message: err2.message,
              stack: err2.stack,
            },
            markup: null,
          });
        } else {
          res.json({
            error: null,
            markup,
          });
        }
      });
    }
  });
});

server.listen(PORT, ADDRESS, () => {
  console.log(`React render server listening at http://${ADDRESS}:${PORT}`);
});
