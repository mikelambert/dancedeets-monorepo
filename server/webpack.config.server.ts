/**
 * Copyright 2016 DanceDeets.
 */

import webpack from 'webpack';
import path from 'path';
import { argv as env } from 'yargs';

const prod = !(env as { debug?: boolean }).debug;

// Bundle all dependencies into the output - no node_modules needed at runtime
// This dramatically reduces deploy size (from 188k files to just the bundles)
// mjml is kept external because it has complex ESM/dynamic requires that webpack 3 can't handle
const externals: Record<string, string> = {
  mjml: 'commonjs mjml',
};

const config: webpack.Configuration = {
  entry: {
    brackets: './assets/js/brackets.js',
    calendar: './assets/js/calendar.js',
    classResults: './assets/js/classResults.js',
    event: './assets/js/event.js',
    eventSearchResults: './assets/js/eventSearchResults.js',
    homepageReact: './assets/js/homepageReact.js',
    mailAddEvent: './assets/js/mailAddEvent.js',
    mailWeeklyNew: './assets/js/mailWeeklyNew.js',
    mailNewUser: './assets/js/mailNewUser.js',
    renderServer: './node_server/renderServer.js',
    topic: './assets/js/topic.js',
    tutorial: './assets/js/tutorial.js',
    tutorialCategory: './assets/js/tutorialCategory.js',
    weeklyMail: './assets/js/weeklyMail.js',
  },
  output: {
    path: path.join(__dirname, 'dist/js-server'),
    filename: '[name].js',
    libraryTarget: 'commonjs2', // Export as module.exports for require()/eval()
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
  externals,
  module: {
    rules: [
      // Note: eslint-loader and shebang-loader removed - not needed for server builds
      {
        test: /\.jsx?$/,
        exclude: /node_modules(?!\/dancedeets-common)/,
        use: {
          loader: 'babel-loader',
          options: {
            babelrc: false, // Ignore .babelrc files in source directories
            presets: [
              [
                '@babel/preset-env',
                {
                  modules: false,
                },
              ],
              '@babel/preset-react',
            ],
            plugins: ['@babel/plugin-transform-flow-strip-types'],
          },
        },
      },
      // Server-side doesn't need actual CSS/images/fonts - use null-loader to ignore them
      {
        test: /\.(png|gif|jpg|jpeg|svg)$/,
        loader: 'null-loader',
      },
      {
        test: /\.s?css$/,
        loader: 'null-loader',
      },
      {
        test: /\.(ttf|otf|eot|woff(2)?)(\?[a-z0-9=.]+)?$/,
        loader: 'null-loader',
      },
    ],
  },
};

export default config;
