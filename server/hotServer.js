
var path = require('path');
var webpack = require('webpack');
var express = require('express');
var proxyMiddleware = require('http-proxy-middleware');
var devMiddleware = require('webpack-dev-middleware');
var hotMiddleware = require('webpack-hot-middleware');
var config = require('./webpack.config.client.babel');

const port = 9090;
const pythonPort = 8080;

// This must match the value we use in base_servlet.py's static_dir
const staticPath = '/dist';

const publicPath = `${staticPath}/js/`;

function enableHotReloading(config) {
  const newEntry = {};
  Object.keys(config.entry).forEach(entryKey => {
    newEntry[entryKey] = [
      'react-hot-loader/patch',
      'webpack-hot-middleware/client',
      config.entry[entryKey],
    ];
  });
  config = {
    ...config,
    entry: newEntry,
    output: {
      ...config.output,
      publicPath,
    },
    plugins: config.plugins.concat([new webpack.HotModuleReplacementPlugin()]),
  };
  return config;
}

var app = express();
var compiler = webpack(enableHotReloading(config));

app.use(devMiddleware(compiler, {
  publicPath,
  hot: true,
  inline: true,
  contentBase: '',
  proxy: {
    '**': {
      target: `http://localhost:${pythonPort}`,
    },
  },
  stats: {
    colors: true,
  },
}));

app.use(hotMiddleware(compiler));

app.use(proxyMiddleware(['**'], {
  target: `http://localhost:${pythonPort}`,
  logLevel: 'error',
}));

app.listen(port, function (err) {
  if (err) {
    return console.error(err);
  }

  console.log(`Listening at http://localhost:${port}/`);
});
