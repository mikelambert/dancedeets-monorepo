
import path from 'path';
import webpack from 'webpack';
import express from 'express';
import proxyMiddleware from 'http-proxy-middleware';
import devMiddleware from 'webpack-dev-middleware';
import hotMiddleware from 'webpack-hot-middleware';
import config from './webpack.config.client.babel';

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

const app = express();
const compiler = webpack(enableHotReloading(config));

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
