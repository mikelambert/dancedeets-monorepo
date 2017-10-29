/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import webpack from 'webpack';
import path from 'path';
import { argv as env } from 'yargs';
import combineLoaders from 'webpack-combine-loaders';

const prod = !env.debug;

module.exports = {
  entry: {
    brackets: './assets/js/brackets.js',
    calendar: './assets/js/calendar.js',
    classResults: './assets/js/classResults.js',
    event: './assets/js/event.js',
    eventSearchResults: './assets/js/eventSearchResults.js',
    mailAddEvent: './assets/js/mailAddEvent.js',
    mailWeeklyNew: './assets/js/mailWeeklyNew.js',
    renderServer: './node_server/renderServer.js',
    topic: './assets/js/topic.js',
    tutorial: './assets/js/tutorial.js',
    tutorialCategory: './assets/js/tutorialCategory.js',
    weeklyMail: './assets/js/weeklyMail.js',
  },
  output: {
    path: path.join(__dirname, 'dist/js-server'),
    filename: '[name].js',
  },
  devtool: prod ? 'source-map' : 'cheap-eval-source-map',
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify(prod ? 'production' : ''),
      },
    }),
  ],
  resolve: {
    extensions: ['.js', '.jsx', '.json'],
  },
  target: 'node',
  node: {
    fs: 'empty',
    net: 'empty',
    child_process: 'empty',
    http: 'empty',
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        use: 'eslint-loader',
        exclude: /node_modules/,
        enforce: 'pre',
      },
      {
        test: /\.jsx?$/,
        include: /node_modules(?!\/dancedeets-common)/,
        loader: 'shebang-loader',
      },
      {
        test: /\.jsx?$/,
        exclude: /node_modules(?!\/dancedeets-common)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              [
                'latest',
                {
                  es2015: {
                    modules: false,
                  },
                },
              ],
              'react',
              'stage-0',
            ],
            plugins: ['transform-flow-strip-types'],
          },
        },
      },
      {
        test: /\.(png|gif)$/,
        use: [
          {
            loader: 'url-loader',
            options: {
              limit: 10000,
              mimetype: 'application/font-woff',
              name: '../img/[name].[ext]',
            },
          },
          {
            loader: 'image-webpack-loader',
            options: {
              bypassOnDebug: true,
              query: {
                optipng: {
                  optimizationLevel: 7,
                },
                gifsicle: {
                  interlaced: false,
                },
              },
            },
          },
        ],
      },
      {
        // This exposes React variable so Chrome React devtools work
        test: require.resolve('react'),
        loader: 'expose-loader?React',
      },
      // We don't care about these on the server too much, but we would like them to avoid erroring-out:
      {
        test: /\.s?css$/,
        use: [
          { loader: 'css-loader?sourceMap' },
          { loader: 'postcss-loader' },
          { loader: 'sass-loader?sourceMap' },
        ],
      },
      {
        test: /\.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9=.]+)?$/,
        use: {
          loader: 'file-loader',
          options: {
            name: '../fonts/[name].[ext]',
          },
        },
      },
    ],
  },
};
