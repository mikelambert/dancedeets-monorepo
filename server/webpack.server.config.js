var webpack = require('webpack');
var path = require('path');

module.exports = {
  entry: {
    'class-results': './assets/js/class-results.js',
    'event': './assets/js/event.js',
    'render_server': './node_server/render_server.js',
  },
  output: {
    path: path.join(__dirname, 'dist/js-server'),
    filename: '[name].js',
  },
  devtool: 'source-map',
  plugins: [
    new webpack.DefinePlugin({
      'process.env': { // eslint-disable-line quote-props
        'NODE_ENV': JSON.stringify('production'),
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
