import webpack from 'webpack';
import ExtractTextPlugin from 'extract-text-webpack-plugin';
import path from 'path';
import uncss from 'uncss';
import { argv as env } from 'yargs';
import combineLoaders from 'webpack-combine-loaders';

function isCommonModule(module) {
  const userRequest = module.userRequest;
  if (typeof userRequest !== 'string') {
    return false;
  }
  const common = ['jquery', 'bootstrap', 'trackjs', '/react/', 'react-dom', 'moment', 'lodash', 'babel-polyfill', '/intl/', 'intl-', 'url', 'fbjs', 'js/messages', 'source-map', 'font-awesome'];
  for (const elem of common) {
    if (userRequest.indexOf(elem) > -1) {
      return true;
    }
  }
  return false;
}

const prod = !env.debug;

const ifProd = plugin => (prod ? plugin : null);

const config = {
  entry: {
    calendar: './assets/js/calendar.js',
    homepage: './assets/js/homepage.js',
    classResultsExec: './assets/js/classResultsExec.js',
    eventExec: './assets/js/eventExec.js',
    eventSearchResultsExec: './assets/js/eventSearchResultsExec.js',
    tutorialExec: './assets/js/tutorialExec.js',
    tutorialCategoryExec: './assets/js/tutorialCategoryExec.js',
  },
  output: {
    path: path.join(__dirname, 'dist/js'),
    filename: '[name].js',
  },
  devtool: prod ? 'source-map' : 'debug',
  plugins: [
    new webpack.ProvidePlugin({
      fetch: 'imports?this=>global!exports?global.fetch!whatwg-fetch',
    }),
    // Only import the english locale for moment.js:
    new webpack.ContextReplacementPlugin(/moment[/\\]locale$/, /en$/),

    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify(prod ? 'production' : ''),
      },
    }),
    new ExtractTextPlugin('../css/[name].css'),
    // Sometimes we get duplicate modules (react-intl, moment)
    // that come from both server/ and common/, and we want to de-dupe them.
    ifProd(new webpack.optimize.DedupePlugin()),
    ifProd(new webpack.optimize.UglifyJsPlugin()),
    new webpack.optimize.CommonsChunkPlugin({
      name: 'common',
      minChunks: isCommonModule,
    }),
  ].filter(x => x),
  resolve: {
    extensions: ['', '.js', '.jsx'],
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
        test: /\.jsx?$/,
        exclude: /(node_modules|bower_components)/,
        loader: combineLoaders([
          {
            loader: 'babel',
            query: {
              presets: ['latest', 'react'],
              plugins: [
                'transform-object-rest-spread',
                'transform-flow-strip-types',
              ],
            },
          },
        ]),
      },
      {
        test: /\.json$/,
        loader: 'json',
      },
      {
        test: /\.s?css$/,
        loader: ExtractTextPlugin.extract('style-loader', ['css-loader?sourceMap', 'pleeease-loader', 'postcss-loader', 'sass-loader?sourceMap']),
      },
      {
        test: /\.png$/,
        loader: combineLoaders([
          {
            loader: 'url',
            query: {
              limit: 10000,
              name: '../img/[name].[ext]',
            },
          },
          {
            loader: 'image-webpack',
            query: {
              bypassOnDebug: true,
              optimizationLevel: 7,
              interlaced: false,
            },
          }
        ]),
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
  postcss: () => [
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
};
module.exports = config;
