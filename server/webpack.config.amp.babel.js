import webpack from 'webpack';
import ExtractTextPlugin from 'extract-text-webpack-plugin';
import path from 'path';
import uncss from 'uncss';
import pleeease from 'pleeease';

module.exports = {
  entry: {
    eventAmp: './assets/js/all-css.js',
  },
  output: {
    path: path.join(__dirname, 'dist-includes/js'),
    filename: '[name].js',
  },
  devtool: 'source-map',
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify('production'),
      },
    }),
    new webpack.optimize.DedupePlugin(),
    new webpack.optimize.UglifyJsPlugin(),
    new ExtractTextPlugin('../css/eventAmp.css'),
  ],
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
        test: /\.jsx?$/,
        exclude: /(node_modules|bower_components)/,
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
        test: /\.s?css$/,
        loader: ExtractTextPlugin.extract('style-loader', ['css-loader?sourceMap,-minimize', 'postcss-loader', 'resolve-url-loader', 'sass-loader?sourceMap']),
      },
      {
        test: /\.png$/,
        loaders: [
          'url-loader?limit=10000&mimetype=application/font-woff&name=../img/[name].[ext]',
          'image-webpack?bypassOnDebug&optimizationLevel=7&interlaced=false',
        ],
      },
      {
        test: /\.jpg$/,
        loader: 'file-loader?name=../img/[name].[ext]',
      },
      {
        test: /\.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9=.]+)?$/,
        loader: 'file-loader?name=../fonts/[name].[ext]',
      },
      {
        // This exposes React variable so Chrome React devtools work
        test: require.resolve('react'),
        loader: 'expose?React',
      },
    ],
  },
  postcss: () => [
    // This handles a bunch for us:
    // sass: Preprocesses your CSS using Sass.
    // autoprefixer: Adds vendor prefixes to CSS, using Autoprefixer.
    // filters: Converts CSS shorthand filters to SVG equivalent
    // rem: Generates pixel fallbacks for rem units
    // pseudoElements: Converts pseudo-elements using CSS3 syntax
    //   (two-colons notation like ::after, ::before, ::first-line and ::first-letter) with the old one
    // opacity: Adds opacity filter for IE8 when using opacity property
    // import: Inlines @import styles, using postcss-import and rebases URLs if needed.
    //
    // We intentionally don't do any minification, since we'd prefer to run uncss first
    pleeease({
      import: false,
      rebase: false,
      minifier: false,
      browsers: ['> 2%'],
    }),
    uncss.postcssPlugin({
      html: ['amp/generated/*.html'],
    }),
  ],
};
