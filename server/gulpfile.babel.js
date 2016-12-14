
// This gulpfile makes use of new JavaScript features.
// Babel handles this without us having to do anything. It just works.
// You can read more about the new JavaScript features here:
// https://babeljs.io/docs/learn-es2015/

import del from 'del';
import favicons from 'gulp-favicons';
import gutil from 'gutil';
import gulp from 'gulp';
import gulpLoadPlugins from 'gulp-load-plugins';
import runSequence from 'run-sequence';
import {output as pagespeed} from 'psi';
import username from 'username';

const $ = gulpLoadPlugins();

const baseAssetsDir = `/Users/${username.sync()}/Dropbox/dancedeets/art/build-assets/`;

gulp.task('compile-favicons', () => gulp
  .src('assets/img/deets-head.png')
  .pipe(favicons({
    appName: 'DanceDeets',
    appDescription: 'Street Dance Events. Worldwide.',
    developerName: 'DanceDeets',
    developerURL: 'http://www.dancedeets.com/',
    background: '#fff',
    path: '/dist/img/favicons/',
    url: 'http://www.dancedeets.com/',
    display: 'standalone',
    orientation: 'portrait',
    version: 1.0,
    logging: false,
    online: true,
    icons: {
      opengraph: false,
      twitter: false,
    },
    html: './dist/templates/favicon_tags.html',
    replace: true,
  }))
  .on('error', gutil.log)
  .pipe(gulp.dest('./dist/img/favicons/'))
);

gulp.task('compile-images-resize', () => gulp
  .src(`${baseAssetsDir}img/**/*.{png,jpg}`)
  .pipe($.responsiveImages({
    'classes/*/*.*': [{
      width: 32,
      height: 32,
      format: 'png',
    }],
    '{location,style}-*.jpg': [{
      width: 450,
      height: 300,
      crop: 'true',
      quality: 60,
    }],
    'deets-activity-*.png': [{
      height: 100,
    }],
    'background*.jpg': [{
      width: 1200,
      quality: 60,
      suffix: '@2x',
    }, {
      width: 600,
      quality: 60,
    }],
    'deets-head-and-title-on-black.png': [{
      height: 64 * 2,
      suffix: '@2x',
    }, {
      height: 64,
    }, {
      height: 60,
      suffix: '-60px',
    }],
    'fb-login.png': [
    {},
    ],
  }))
  .pipe($.imagemin({
    progressive: true,
    interlaced: true,
  }))
  .pipe(gulp.dest('dist/img'))
);

gulp.task('compile-images', ['compile-favicons', 'compile-images-resize', 'compile-svg']);

// gets deets-activity svg files
gulp.task('compile-svg', () => gulp
  .src(`${baseAssetsDir}img/*.svg`)
  .pipe($.cache($.imagemin({
    progressive: true,
    interlaced: true,
  })))
  .pipe(gulp.dest('dist/img'))
);

gulp.task('compile-fonts', () => gulp
  .src('bower_components/font-awesome/fonts/*.*')
    .pipe(gulp.dest('dist/fonts/'))
);

// Run PageSpeed Insights
gulp.task('pagespeed', cb =>
  // Update the below URL to the public URL of your site
  pagespeed('http://www.dancedeets.com/new_homepage', {
    strategy: 'mobile',
    // By default we use the PageSpeed Insights free (no API key) tier.
    // Use a Google Developer API key if you have one: http://goo.gl/RkN0vE
    // key: 'YOUR_API_KEY'
  }, cb)
);

gulp.task('generate-amp-sources', $.shell.task(['./amp/generate_amp_sources.py']));

function webpack(configName, dependencies = []) {
  const webpackCommand = `webpack --color --progress --config webpack.config.${configName}.babel.js`;
  gulp.task(`compile-webpack-${configName}`, dependencies, $.shell.task([webpackCommand]));
  gulp.task(`compile-webpack-${configName}-watch`, dependencies, $.shell.task([`${webpackCommand} --watch`]));
}
// Generate rules for our three webpack configs
webpack('amp', ['generate-amp-sources']);
webpack('server');
webpack('client');

gulp.task('compile-css-js', ['compile-webpack-amp', 'compile-webpack-server', 'compile-webpack-client']);

gulp.task('compile', ['compile-css-js', 'compile-images', 'compile-fonts']);

gulp.task('clean', () => del.sync('dist'));

gulp.task('test', $.shell.task(['./nose.sh']));

gulp.task('clean-build-test', (callback) => {
  runSequence('clean', 'compile', 'test', callback);
});

// Someday we may want something more elaborate like:
// https://github.com/gulpjs/gulp/blob/master/docs/recipes/automate-release-workflow.md
gulp.task('deploy', ['clean-build-test'], $.shell.task(['./deploy.sh']));

