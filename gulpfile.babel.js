
'use strict';

// This gulpfile makes use of new JavaScript features.
// Babel handles this without us having to do anything. It just works.
// You can read more about the new JavaScript features here:
// https://babeljs.io/docs/learn-es2015/


import autoprefixer from 'autoprefixer';
import browserify from 'browserify';
import buffer from 'vinyl-buffer';
import del from 'del';
import gulp from 'gulp';
import gulpLoadPlugins from 'gulp-load-plugins';
import gutil from 'gutil';
import os from 'os';
import path from 'path';
import reactify from 'reactify';
import runSequence from 'run-sequence';
import source from 'vinyl-source-stream';
import watchify from 'watchify';
import username from 'username';
import {output as pagespeed} from 'psi';

import gulpif from 'gulp-if';
var concat = require('gulp-concat');
var cssnano = require('gulp-cssnano');
var lodash = require('lodash')
var rename = require('gulp-rename');
var responsive = require('gulp-responsive-images');
var postcss = require('gulp-postcss');
var sass = require('gulp-sass');
var shell = require('gulp-shell');
var sourcemaps = require('gulp-sourcemaps');
var uglify = require('gulp-uglify');
var uncss = require('gulp-uncss');

const $ = gulpLoadPlugins();

var baseAssetsDir = '/Users/' + username.sync() + '/Dropbox/dancedeets-art/build-assets/'

var src  = './';
var dest = './dist';
var config = {
  javascript: {
    rootFiles: [
      {
        src  : src + '/assets/js/main.js',
        dest : 'main.js'
      },
      {
        src  : src + '/assets/js/ie8.js',
        dest : 'ie8.js'
      },
    ],
    dest: dest + '/js'
  },
  css: {
    sourceFiles: [
        "node_modules/font-awesome/css/font-awesome.css",
        "node_modules/bootstrap/dist/css/bootstrap.css",
        "node_modules/animate.css/animate.css",
        "assets/css/app.css",
        "assets/css/style.css",
        "assets/css/headers/header-v6.css",
        "assets/css/footers/footer-v2.css",
        "assets/css/colors.scss",
        "assets/css/custom.css",
    ],
    comboFile: 'main.css',
    dest: dest + '/css',
    destDebug: dest + '/css-debug',

    // uncss parameters
    uncssArgs: {
        ignore: [
            '.animated.flip',
            new RegExp('.header-v6(.header-dark-transparent)?.header-fixed-shrink'),
        ],
        html: [
            'templates/new_homepage.html'
        ]
    }
  }
};


// Lint JavaScript
gulp.task('lint', () => {
  return gulp.src('assets/js/**/*.js')
    .pipe($.eslint())
    .pipe($.eslint.format())
    .pipe($.eslint.failAfterError())
});

// Do we want this?
//    .pipe($.newer('.tmp/styles'))
function compileCssTo(destDir, destFilename) {
    return () => {
        return gulp.src(config.css.sourceFiles)
            .pipe($.sourcemaps.init())
                .pipe($.sass({
                    'precision': 10
                }).on('error', $.sass.logError))
                .pipe($.autoprefixer({
                    browsers: ['> 2%']
                }))
                .pipe($.if(destFilename != null, concat(destFilename || 'dummyArgSoConstructorPasses')))
                .pipe(gulp.dest(destDir))
                .pipe($.uncss(config.css.uncssArgs))
                .pipe($.rename({ extname: '.trim.css' }))
                .pipe(gulp.dest(destDir))
                .pipe($.cssnano())
                .pipe($.size({title: 'styles'}))
                .pipe($.rename({ extname: '.min.css', basename: path.basename(config.css.comboFile, '.css') }))
                .pipe(gulp.dest(destDir))
            .pipe($.sourcemaps.write('.'));
    }
}



gulp.task('compile-css', compileCssTo(config.css.dest, 'main.css'));
gulp.task('compile-css-individual-debug', compileCssTo(config.css.destDebug));

gulp.task('compile-js', compileJavascript(false));
gulp.task('watchify', compileJavascript(true));

function compileJavascript(watch) {
  return function(callback) {
    var files = config.javascript.rootFiles;

    files.forEach(function (file) {
      var b = browserify({
          entries: file.src, // Only need initial file, browserify finds the deps
          debug: true        // Enable sourcemaps
      });
      // Optionally start a long-lived watchify session
      if (watch) {
        b = watchify(b);
      }
      // Output build logs to terminal
      b.on('log', gutil.log);

      // Convert JSX, if we see it
      b.transform(reactify);

      function buildBundle() {
        return b.bundle()
          .pipe(source(file.dest))
          .pipe(buffer())
          .pipe(gulp.dest(config.javascript.dest))
          .pipe($.sourcemaps.init({loadMaps: true}))
            .pipe($.babel())
            .pipe($.uglify())
            .on('error', gutil.log)
            .pipe($.rename({ extname: '.min.js' }))
            .pipe($.size({title: 'scripts'}))
          .pipe($.sourcemaps.write('.'))

          .pipe(gulp.dest(config.javascript.dest));
      }
      // On any dependency update, re-runs the bundler
      b.on('update', buildBundle);
      // And we need to run the builder once, to start things off.
      return buildBundle();
    });

    callback();
  };
}

gulp.task('compile-images-resize', () => {
  return gulp.src(baseAssetsDir + 'img/**/*.{png,jpg}')
    .pipe($.responsiveImages({
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
        height: 64*2,
        suffix: '@2x',
      }, {
        height: 64,
      }],
    }))
    .pipe($.imagemin({
      progressive: true,
      interlaced: true
    }))
    .pipe(gulp.dest('dist/img'));
});

gulp.task('compile-images', ['compile-images-resize', 'compile-svg', 'compile-icons']);

// gets deets-activity svg files
gulp.task('compile-svg', () => {
  return gulp.src(baseAssetsDir + 'img/*.svg')
    .pipe($.cache($.imagemin({
      progressive: true,
      interlaced: true
    })))
    .pipe(gulp.dest('dist/img'));
});

gulp.task('compile-icons', () => {
  return gulp.src('assets/img/icons/social/*.png')
    .pipe($.cache($.imagemin({
      progressive: true,
      interlaced: true
    })))
    .pipe(gulp.dest('dist/img/icons/social/'));
});

gulp.task('compile-fonts', () => {
  return gulp.src('bower_components/font-awesome/fonts/*.*')
    .pipe(gulp.dest('dist/fonts/'));
});


// Run PageSpeed Insights
gulp.task('pagespeed', cb =>
  // Update the below URL to the public URL of your site
  pagespeed('http://www.dancedeets.com/new_homepage', {
    strategy: 'mobile'
    // By default we use the PageSpeed Insights free (no API key) tier.
    // Use a Google Developer API key if you have one: http://goo.gl/RkN0vE
    // key: 'YOUR_API_KEY'
  }, cb)
);


gulp.task('compile', ['compile-js', 'compile-css', 'compile-images', 'compile-fonts']);

gulp.task('clean', () => {
  return del.sync('dist');
})

gulp.task('test', $.shell.task(['./nose.sh']));

gulp.task('clean-build-test', function (callback) {
    runSequence('clean', 'compile', 'lint', 'test', callback);
});

// TODO: someday we may want something more elaborate like:
// https://github.com/gulpjs/gulp/blob/master/docs/recipes/automate-release-workflow.md
gulp.task('deploy', ['clean-build-test'], $.shell.task(['./deploy.sh']));
