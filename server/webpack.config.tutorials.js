/**
 * Minimal webpack config for tutorials MVP
 * Skip eslint, use minimal babel config
 */

const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: {
    tutorialExec: './assets/js/tutorialExec.js',
    tutorialCategoryExec: './assets/js/tutorialCategoryExec.js',
  },
  output: {
    path: path.join(__dirname, 'dist/js'),
    filename: '[name].js',
  },
  devtool: 'cheap-source-map',
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        REACT_SPINKIT_NO_STYLES: JSON.stringify(true),
        NODE_ENV: JSON.stringify('development'),
        BROWSER: JSON.stringify(true),
      },
    }),
    // Only import the english locale for moment.js
    new webpack.ContextReplacementPlugin(/moment[/\\]locale$/, /en$/),
  ],
  resolve: {
    extensions: ['.js', '.jsx', '.json'],
    modules: [
      path.resolve(__dirname, 'node_modules'),
      'node_modules',
    ],
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules(?!\/dancedeets-common)/,
        use: {
          loader: 'babel-loader',
          options: {
            babelrc: false,
            presets: [
              [require.resolve('@babel/preset-env'), { modules: false }],
              require.resolve('@babel/preset-react'),
            ],
            plugins: [
              require.resolve('@babel/plugin-transform-flow-strip-types'),
            ],
          },
        },
      },
      // Handle CSS imports - just ignore for now (inline styles used)
      {
        test: /\.s?css$/,
        use: 'null-loader',
      },
      // Handle images
      {
        test: /\.(png|gif|jpg|svg)$/,
        use: {
          loader: 'url-loader',
          options: {
            limit: 10000,
            name: '../img/[name].[ext]',
          },
        },
      },
      // Handle fonts
      {
        test: /\.(ttf|otf|eot|woff(2)?)(\?[a-z0-9=.]+)?$/,
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
