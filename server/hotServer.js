
import path from 'path';
import webpack from 'webpack';
import express from 'express';
import proxyMiddleware from 'http-proxy-middleware';
import devMiddleware from 'webpack-dev-middleware';
import hotMiddleware from 'webpack-hot-middleware';
import config from './webpack.config.client.babel';
import yargs from 'yargs';

const argv = yargs
  .option('p', {
    alias: 'port',
    description: 'Specify the server\'s port',
    default: 9090,
  })
  .option('b', {
    alias: 'backend',
    description: 'Specify the backend server\'s port',
    default: 8080,
  })
  .option('a', {
    alias: 'address',
    description: 'Specify the server\'s address',
    default: '127.0.0.1',
  })
  .help('h').alias('h', 'help')
  // We don't want a strict server, since we want some flags falling-through to the webpack config
  // .strict()
  .argv;

const port = argv.port;
const pythonPort = argv.backend;

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
