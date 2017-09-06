/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import webpack from 'webpack';
import ExtractTextPlugin from 'extract-text-webpack-plugin';
import path from 'path';
import uncss from 'uncss';
import pleeease from 'pleeease';
import { argv as env } from 'yargs';
import OptimizeCssAssetsPlugin from 'optimize-css-assets-webpack-plugin';

const prod = !env.debug;

export default function uncssWebpackGenerator(outputFilename, htmlFiles) {
  return {
    entry: {
      dummy: './assets/js/all-css.js',
    },
    output: {
      path: path.join(__dirname, 'dist-includes/js'),
      filename: '[name].js',
    },
    devtool: prod ? 'source-map' : 'cheap-eval-source-map',
    plugins: [
      new webpack.DefinePlugin({
        'process.env': {
          NODE_ENV: JSON.stringify('production'),
        },
      }),
      new webpack.optimize.UglifyJsPlugin({
        sourceMap: true,
        compress: {
          warnings: true,
        },
      }),
      new ExtractTextPlugin({
        filename: `../css/${outputFilename}.css`,
      }),
      new OptimizeCssAssetsPlugin({
        // Removing all comments because we're saving this to minimified AMP files with size limits
        cssProcessorOptions: { discardComments: { removeAll: true } },
        canPrint: true,
      }),
    ],
    resolve: {
      extensions: ['.js', '.jsx'],
    },
    module: {
      rules: [
        {
          test: /\.jsx?$/,
          use: 'eslint-loader',
          exclude: /node_modules(?!\/dancedeets-common)/,
          enforce: 'pre',
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
          test: /\.s?css$/,
          use: ExtractTextPlugin.extract({
            fallback: 'style-loader',
            use: [
              {
                loader: 'css-loader',
                options: {
                  sourceMap: true,
                },
              },
              {
                loader: 'postcss-loader',
                options: {
                  plugins: () => [
                    // This handles a bunch for us:
                    // autoprefixer: Adds vendor prefixes to CSS, using Autoprefixer.
                    // filters: Converts CSS shorthand filters to SVG equivalent
                    // rem: Generates pixel fallbacks for rem units
                    // pseudoElements: Converts pseudo-elements using CSS3 syntax
                    //   (two-colons notation like ::after, ::before, ::first-line and ::first-letter) with the old one
                    // opacity: Adds opacity filter for IE8 when using opacity property
                    //
                    // We intentionally don't do any minification, since we'd prefer to run uncss first
                    pleeease({
                      import: false,
                      rebaseUrls: false,
                      minifier: false,
                      browsers: ['> 2%'],
                    }),
                    uncss.postcssPlugin({
                      html: [...htmlFiles, 'amp/empty.html'],
                    }),
                  ],
                },
              },
              { loader: 'sass-loader?sourceMap' },
            ],
          }),
        },
        {
          test: /\.png$/,
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
          test: /\.jpg$/,
          use: {
            loader: 'file-loader',
            options: {
              name: '../img/[name].[ext]',
            },
          },
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
        {
          // This exposes React variable so Chrome React devtools work
          test: require.resolve('react'),
          loader: 'expose-loader?React',
        },
      ],
    },
  };
}
