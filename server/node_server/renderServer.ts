/**
 * Copyright 2016 DanceDeets.
 */

import fs from 'fs';
import http from 'http';
import express, { Request, Response } from 'express';
import bodyParser from 'body-parser';
import React from 'react';
import ReactDOMServer from 'react-dom/server';

// mjml is kept as external in esbuild config since it uses dynamic requires.
// Email rendering will fail if mjml is not installed, but SSR will still work.
let mjml: ((mjmlData: string) => { html: string }) | null = null;
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

app.get('/', (req: Request, res: Response) => {
  res.end('React render server');
});

interface ComponentModule {
  default: React.ComponentType<any>;
  HelmetRewind?: () => Record<string, { toString: () => string }>;
}

interface SerializedHead {
  [key: string]: string;
}

function serializedHead(component: ComponentModule | null): SerializedHead | null {
  if (!component || !component.HelmetRewind) {
    return null;
  }
  const head = component.HelmetRewind();
  const serialized: SerializedHead = {};
  Object.keys(head).forEach(key => {
    serialized[key] = head[key].toString();
  });
  return serialized;
}

// Cache for loaded components to avoid re-reading files
const componentCache: Record<string, ComponentModule> = {};

interface RenderRequest {
  path: string;
  props: Record<string, any>;
  toStaticMarkup?: boolean;
}

interface RenderResponse {
  error: { type: string; message: string; stack?: string } | null;
  markup: string | null;
  head?: SerializedHead | null;
}

app.post('/render', (req: Request, res: Response) => {
  const { path: componentPath, props, toStaticMarkup } = req.body as RenderRequest;

  fs.readFile(componentPath, { encoding: 'utf8' }, (err, data) => {
    if (err) {
      const response: RenderResponse = {
        error: {
          type: err.constructor.name,
          message: err.message,
          stack: err.stack,
        },
        markup: null,
      };
      res.json(response);
      return;
    }

    let component: ComponentModule | null = null;
    let Component: React.ComponentType<any> | null = null;

    try {
      // Evaluate the bundle to get the component module
      // The bundle exports { default: ComponentClass, HelmetRewind?: function }
      component = eval(data); // eslint-disable-line no-eval
      Component = component!.default;
    } catch (e) {
      console.error('Error evaluating component:', e);
      const error = e as Error;
      const response: RenderResponse = {
        error: {
          type: error.constructor.name,
          message: error.message,
          stack: error.stack,
        },
        markup: null,
      };
      res.json(response);
      return;
    }

    try {
      // Create the React element with props
      const element = React.createElement(Component!, props);

      // Render to string or static markup
      const markup = toStaticMarkup
        ? ReactDOMServer.renderToStaticMarkup(element)
        : ReactDOMServer.renderToString(element);

      // Get Helmet head data if available
      const head = serializedHead(component);

      const response: RenderResponse = {
        error: null,
        markup,
        head,
      };
      res.json(response);
    } catch (e) {
      console.error('Error rendering component:', e);
      const error = e as Error;
      const response: RenderResponse = {
        error: {
          type: error.constructor.name,
          message: error.message,
          stack: error.stack,
        },
        markup: null,
      };
      res.json(response);
    }
  });
});

interface MjmlRequest {
  mjml: string;
}

interface MjmlResponse {
  error: { message: string } | null;
  html: string | null;
}

app.post('/mjml-render', (req: Request, res: Response) => {
  if (!mjml) {
    const response: MjmlResponse = {
      error: { message: 'mjml not available - please install mjml package' },
      html: null,
    };
    res.json(response);
    return;
  }
  const mjmlData = (req.body as MjmlRequest).mjml;
  const result = mjml(mjmlData);
  const response: MjmlResponse = {
    error: null,
    html: result.html,
  };
  res.json(response);
});

server.listen(PORT, ADDRESS, () => {
  console.log(
    `Node (react, mjml) server listening at http://${ADDRESS}:${PORT}`
  );
});
