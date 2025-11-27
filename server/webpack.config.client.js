/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

const webpack = require('webpack');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');
const ChunkManifestPlugin = require('chunk-manifest-webpack-plugin');
const WebpackMd5Hash = require('webpack-md5-hash');
const path = require('path');
const { argv: env } = require('yargs');
const pleeease = require('pleeease');

function isJQuery(module) {
  const userRequest = module.userRequest;
  if (typeof userRequest !== 'string') {
    return false;
  }
  if (userRequest.endsWith('css')) {
    return false; // leave it in the parent commons.sccchunk
  }
  const common = ['jquery'];
  for (const elem of common) {
    if (userRequest.indexOf(elem) > -1) {
      return true;
    }
  }
  return false;
}

const prod = !env.debug;

const ifProd = plugin => (prod ? plugin : null);

const entry = {
  addEvent: './assets/js/addEvent.js',
  bracketsExec: './assets/js/bracketsExec.js',
  calendarExec: './assets/js/calendarExec.js',
  homepageReact: './assets/js/homepageReactExec.js',
  homepage: './assets/js/homepage.js',
  normalPage: './assets/js/normalPage.js',
  classResultsExec: './assets/js/classResultsExec.js',
  eventExec: './assets/js/eventExec.js',
  eventSearchResultsExec: './assets/js/eventSearchResultsExec.js',
  topicExec: './assets/js/topicExec.js',
  tutorialExec: './assets/js/tutorialExec.js',
  tutorialCategoryExec: './assets/js/tutorialCategoryExec.js',
};

const config = {
  entry,
  output: {
    path: path.join(__dirname, 'dist/js'),
    filename: prod ? '[name].[chunkhash].js' : '[name].js',
    chunkFilename: prod ? '[name].[chunkhash].js' : '[name].js',
  },
  devtool: prod ? 'source-map' : 'cheap-eval-source-map',
  plugins: [
    new webpack.ProvidePlugin({
      fetch:
        'imports-loader?this=>global!exports-loader?global.fetch!whatwg-fetch',
    }),
    // Only import the english locale for moment.js:
    new webpack.ContextReplacementPlugin(/moment[/\\]locale$/, /en$/),

    new webpack.DefinePlugin({
      'process.env': {
        REACT_SPINKIT_NO_STYLES: JSON.stringify(true), // Import just the spinners we care about
        NODE_ENV: JSON.stringify(prod ? 'production' : ''),
        BROWSER: JSON.stringify(true),
      },
    }),
    new ExtractTextPlugin({
      filename: prod ? '../css/[name].[contenthash].css' : '../css/[name].css',
    }),
    new webpack.optimize.CommonsChunkPlugin({
      name: 'jquery',
      // For now this is *after* 'common', and so gets loaded first.
      // When we move jquery out of assets/js/common.js, we can flip these.
      chunks: ['common', ...Object.keys(entry)],
      minChunks: isJQuery,
    }),
    new webpack.optimize.CommonsChunkPlugin({
      name: 'common',
      chunks: ['homepage', 'normalPage', 'eventExec', 'eventSearchResultsExec'],
      minChunks: 2,
    }),
    new webpack.optimize.ModuleConcatenationPlugin(),
    ifProd(
      new webpack.optimize.UglifyJsPlugin({
        sourceMap: true,
        compress: {
          warnings: true,
        },
      })
    ),
    ifProd(
      new OptimizeCssAssetsPlugin({
        canPrint: false,
      })
    ),
    ifProd(new webpack.HashedModuleIdsPlugin()),
    ifProd(new WebpackMd5Hash()),
    ifProd(
      new ManifestPlugin({
        fileName: '../manifest.json',
      })
    ),
    ifProd(
      new ChunkManifestPlugin({
        filename: '../chunk-manifest.json',
        manifestVariable: 'webpackManifest',
      })
    ),
  ].filter(x => x),
  resolve: {
    extensions: ['.js', '.jsx'],
  },
  module: {
    rules: [
      // Disabled eslint-loader due to eslint version incompatibilities
      // {
      //   test: /\.jsx?$/,
      //   use: 'eslint-loader',
      //   exclude: /node_modules(?!\/dancedeets-common)/,
      //   enforce: 'pre',
      // },
      {
        test: /\.jsx?$/,
        exclude: /node_modules(?!\/dancedeets-common)/,
        use: {
          loader: 'babel-loader',
          options: {
            babelrc: false, // Don't use .babelrc files from dancedeets-common
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
                  /* uncss.postcssPlugin({
                    ignore: [
                      '.animated',
                      '.animated.flip',
                      new RegExp('\\.alert\w+\\b'),
                      new RegExp('\\.(in|open|collapsing)\\b'),
                      new RegExp('\\.header-v6(\\.header-dark-transparent)?\\.header-fixed-shrink'),
                    ],
                    html: ['example_html/new_homepage.html'],
                  }),*/
                ],
              },
            },
            {
              loader: 'sass-loader',
              options: {
                sourceMap: true,
                implementation: require('sass'),
              },
            },
          ],
        }),
      },
      {
        test: /\.(png|gif)$/,
        use: [
          {
            loader: 'url-loader',
            options: {
              limit: 10000,
              name: '../img/[name].[ext]',
            },
          },
          // Disabled image-webpack-loader - binaries not installed with --ignore-scripts
          // {
          //   loader: 'image-webpack-loader',
          //   options: {
          //     bypassOnDebug: true,
          //     query: {
          //       optipng: {
          //         optimizationLevel: 7,
          //       },
          //       gifsicle: {
          //         interlaced: false,
          //       },
          //     },
          //   },
          // },
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
        use: 'expose-loader?React',
      },
    ],
  },
};
module.exports = config;
