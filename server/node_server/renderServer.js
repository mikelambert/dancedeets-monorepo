/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import fs from 'fs';
import http from 'http';
import express from 'express';
import bodyParser from 'body-parser';
import reactRender from 'react-render';
// mjml is kept as external in webpack config since it uses ES6+ syntax
// that can't be bundled. Email rendering will fail if mjml is not installed,
// but SSR will still work.
let mjml2html = null;
try {
  mjml2html = require('mjml').mjml2html;
} catch (e) {
  console.log('mjml not available - email rendering disabled');
}

// Use environment variables or defaults for Docker deployment
// This replaces yargs which doesn't bundle well with webpack
const ADDRESS = process.env.RENDER_SERVER_ADDRESS || '0.0.0.0';
const PORT = parseInt(process.env.RENDER_SERVER_PORT || '8090', 10);

const app = express();
const server = new http.Server(app);

app.use(
  bodyParser.json({
    limit: '10mb', // This is an internal-only server, so we can really handle arbitrary amounts of data
  })
);

app.get('/', (req, res) => {
  res.end('React render server');
});

function serializedHead(component) {
  if (!component || !component.HelmetRewind) {
    return null;
  }
  const head = component.HelmetRewind();
  const serialized = {};
  Object.keys(head).forEach(key => {
    serialized[key] = head[key].toString();
  });
  return serialized;
}

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
      const { body } = req;
      let component = null;
      // We list this here, so that it applies for the eval.
      // But we don't list it at the top, because any attempt to inline this code
      // will trigger runtime errors on the compiled JS.
      if (!global._babelPolyfill) {
        require('babel-polyfill'); // eslint-disable-line global-require
      }
      // Ensure this runs in a try-catch, so the server cannot die on eval()ing code.
      try {
        component = eval(data); // eslint-disable-line no-eval
        body.component = component.default;
      } catch (e) {
        console.error(e);
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
        const head = serializedHead(component);
        if (err2) {
          console.error(err2);
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
            head,
          });
        }
      });
    }
  });
});

app.post('/mjml-render', (req, res) => {
  if (!mjml2html) {
    res.json({
      error: { message: 'mjml not available in bundled mode' },
      html: null,
    });
    return;
  }
  const mjmlData = req.body.mjml;
  const html = mjml2html(mjmlData);
  res.json({
    error: null,
    html,
  });
});
server.listen(PORT, ADDRESS, () => {
  console.log(
    `Node (react, mjml) server listening at http://${ADDRESS}:${PORT}`
  );
});
