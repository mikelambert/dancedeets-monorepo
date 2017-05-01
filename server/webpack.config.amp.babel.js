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
    new webpack.optimize.UglifyJsPlugin({
      sourceMap: true,
      compress: {
        warnings: true
      },
    }),
    new ExtractTextPlugin({
      filename: '../css/eventAmp.css',
    }),
  ],
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
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              ["latest", {
                "es2015": {
                  "modules": false,
                },
              }],
              'react',
              'stage-0',
            ],
            plugins: [
              'transform-flow-strip-types',
            ],
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
                minimize: true,
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
                    html: ['amp/generated/*.html', 'amp/empty.html'],
                  }),
                ],
              },
            },
            {loader: 'sass-loader?sourceMap'},
          ]
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
              optimizationLevel: 7,
              interlaced: false,
            },
          },
        ],
      },
      {
        test: /\.jpg$/,
        use: {
          loader: 'file-loader',
          options: {
            'name': '../img/[name].[ext]',
          },
        },
      },
      {
        test: /\.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9=.]+)?$/,
        use: {
          loader: 'file-loader',
          options: {
            'name': '../fonts/[name].[ext]',
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
