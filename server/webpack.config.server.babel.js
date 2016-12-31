import webpack from 'webpack';
import path from 'path';
import { argv as env } from 'yargs';

const prod = !env.debug;

module.exports = {
  entry: {
    brackets: './assets/js/brackets.js',
    classResults: './assets/js/classResults.js',
    event: './assets/js/event.js',
    eventSearchResults: './assets/js/eventSearchResults.js',
    renderServer: './node_server/renderServer.js',
    tutorial: './assets/js/tutorial.js',
    tutorialCategory: './assets/js/tutorialCategory.js',
  },
  output: {
    path: path.join(__dirname, 'dist/js-server'),
    filename: '[name].js',
  },
  devtool: prod ? 'source-map' : 'eval',
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify(prod ? 'production' : ''),
      },
    }),
  ],
  resolve: {
    extensions: ['', '.js', '.jsx', '.json'],
  },
  target: 'node',
  node: {
    fs: 'empty',
    net: 'empty',
    child_process: 'empty',
    http: 'empty',
  },
  module: {
    preLoaders: [
      {
        test: /\.jsx?$/,
        loader: 'eslint-loader',
        exclude: /node_modules/,
      },
    ],
    loaders: [
      {
        test: /\.json$/,
        loader: 'json',
      },
      {
        test: /\.jsx?$/,
        exclude: /node_modules(?!\/dancedeets-common)/,
        loader: 'babel',
        query: {
          presets: ['latest', 'react'],
          plugins: [
            'transform-object-rest-spread',
            'transform-flow-strip-types',
          ],
        },
      },
      {
        test: /\.png$/,
        loaders: [
          'url-loader?limit=10000&mimetype=application/font-woff&name=../img/[name].[ext]',
          'image-webpack?bypassOnDebug&optimizationLevel=7&interlaced=false',
        ],
      },
      {
        // This exposes React variable so Chrome React devtools work
        test: require.resolve('react'),
        loader: 'expose?React',
      },
    ],
  },
};
