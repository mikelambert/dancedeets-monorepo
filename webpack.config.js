var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var path = require('path');
var postcssImport = require('postcss-import');
var uncss = require('uncss');

module.exports = {
  entry: {
    main: './assets/js/main.js',
    ie8: './assets/js/ie8.js',
  },
  output: {
    path: path.join(__dirname, "dist/js"),
    filename: '[name].js',
  },
  devtool: 'source-map',
  plugins: [
    new webpack.optimize.DedupePlugin(),
    new webpack.optimize.UglifyJsPlugin(),
    new ExtractTextPlugin('../css/[name].css'),
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
          presets: ['react', 'es2015'],
        },
      },
      {
        test: /\.s?css$/,
        loader: ExtractTextPlugin.extract('style-loader', ['css-loader?sourceMap', 'sass-loader', 'pleeease-loader', 'postcss-loader']),
      },
      {
        test: /\.png$/,
        loader: 'file-loader?name=../img/[name].[ext]',
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
  pleeease: {
    import: false,
    rebase: false,
    minifier: false,
    browsers: ['> 2%'],
  },
  postcss: function() {
    return [
      // TODO: maybe we want to do this here, so imports get counted against webpack depedencies for reloading?
      //postcssImport({
      //  addDependencyTo: webpack,
      //}),
      uncss.postcssPlugin({
        ignore: [
          '.animated',
          '.animated.flip',
          new RegExp('.header-v6(.header-dark-transparent)?.header-fixed-shrink'),
        ],
        html: ['templates/new_homepage.html'],
      }),
    ];
  },
};
