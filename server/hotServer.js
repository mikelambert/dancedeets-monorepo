
var path = require('path');
var webpack = require('webpack');
var express = require('express');
var proxyMiddleware = require('http-proxy-middleware');
var devMiddleware = require('webpack-dev-middleware');
var hotMiddleware = require('webpack-hot-middleware');
require('babel-core/register');
require('babel-polyfill');
var config = require('./webpack.config.client.babel');

var app = express();
var compiler = webpack(config);

app.use(devMiddleware(compiler, {
  publicPath: '/dist/js/',
  hot: true,
  inline: true,
  contentBase: '',
  proxy: {
    '**': {
      target: 'http://localhost:8080',
    },
  },
  stats: {
    colors: true,
  },
}));

app.use(hotMiddleware(compiler));

app.use(proxyMiddleware(['**'], {
  target: 'http://localhost:8080',
  logLevel: 'error',
}));
/*
app.get('*', function (req, res) {
  res.sendFile(path.join(__dirname, 'index.html'));
});
*/
app.listen(9090, function (err) {
  if (err) {
    return console.error(err);
  }

  console.log('Listening at http://localhost:9090/');
});
