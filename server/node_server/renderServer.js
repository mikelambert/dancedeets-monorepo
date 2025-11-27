/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import fs from 'fs';
import http from 'http';
import express from 'express';
import bodyParser from 'body-parser';
import React from 'react';
import ReactDOMServer from 'react-dom/server';

// mjml is kept as external in esbuild config since it uses dynamic requires.
// Email rendering will fail if mjml is not installed, but SSR will still work.
let mjml = null;
try {
  mjml = require('mjml');
} catch (e) {
  console.log('mjml not available - email rendering disabled');
}

// Use environment variables or defaults for Docker deployment
const ADDRESS = process.env.RENDER_SERVER_ADDRESS || '0.0.0.0';
const PORT = parseInt(process.env.RENDER_SERVER_PORT || '8090', 10);

const app = express();
const server = new http.Server(app);

app.use(
  bodyParser.json({
    limit: '10mb', // This is an internal-only server, so we can handle large payloads
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

// Cache for loaded components to avoid re-reading files
const componentCache = {};

app.post('/render', (req, res) => {
  const { path: componentPath, props, toStaticMarkup } = req.body;

  fs.readFile(componentPath, { encoding: 'utf8' }, (err, data) => {
    if (err) {
      res.json({
        error: {
          type: err.constructor.name,
          message: err.message,
          stack: err.stack,
        },
        markup: null,
      });
      return;
    }

    let component = null;
    let Component = null;

    try {
      // Evaluate the bundle to get the component module
      // The bundle exports { default: ComponentClass, HelmetRewind?: function }
      component = eval(data); // eslint-disable-line no-eval
      Component = component.default;
    } catch (e) {
      console.error('Error evaluating component:', e);
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

    try {
      // Create the React element with props
      const element = React.createElement(Component, props);

      // Render to string or static markup
      const markup = toStaticMarkup
        ? ReactDOMServer.renderToStaticMarkup(element)
        : ReactDOMServer.renderToString(element);

      // Get Helmet head data if available
      const head = serializedHead(component);

      res.json({
        error: null,
        markup,
        head,
      });
    } catch (e) {
      console.error('Error rendering component:', e);
      res.json({
        error: {
          type: e.constructor.name,
          message: e.message,
          stack: e.stack,
        },
        markup: null,
      });
    }
  });
});

app.post('/mjml-render', (req, res) => {
  if (!mjml) {
    res.json({
      error: { message: 'mjml not available - please install mjml package' },
      html: null,
    });
    return;
  }
  const mjmlData = req.body.mjml;
  const result = mjml(mjmlData);
  res.json({
    error: null,
    html: result.html,
  });
});

server.listen(PORT, ADDRESS, () => {
  console.log(
    `Node (react, mjml) server listening at http://${ADDRESS}:${PORT}`
  );
});
