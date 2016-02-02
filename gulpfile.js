var browserify = require('browserify');
var buffer     = require('vinyl-buffer');
var concat = require('gulp-concat');
var cssnano = require('gulp-cssnano');
var debowerify = require("debowerify");
var del = require('del');
var gulp = require('gulp');
var gutil = require('gutil');
var lodash = require('lodash')
var os = require("os");
var path = require('path');
var reactify   = require('reactify');
var rename = require('gulp-rename');
var responsive = require('gulp-responsive-images');
var source     = require('vinyl-source-stream');
var sourcemaps = require('gulp-sourcemaps');
var uglify = require('gulp-uglify');
var uncss = require('gulp-uncss');
var watchify = require('watchify');
const username = require('username')


var baseAssetsDir = '/Users/' + username.sync() + '/Dropbox/dancedeets-art/build-assets/'


var src  = './';
var dest = './dist';
var config = {
  javascript: {
    rootFiles: [
      {
        src  : src + '/main.js',
        dest : 'main.js'
      },
      {
        src  : src + '/ie8.js',
        dest : 'ie8.js'
      },
    ],
    dest: dest + '/js'
  },
  css: {
    bowerSourceFiles: [
        // url() will be relative to the first file,
        // so let's prioritize font-awesome since it references font files
        "bower_components/font-awesome/css/font-awesome.css",
        "bower_components/bootstrap/dist/css/bootstrap.css",
        "bower_components/animate.css/animate.css",
    ],
    assetsSourceFiles: [
        // url() will be relative to the first file I think,
        // so let's prioritize app since it references social-icon images
        "assets/css/app.css",
        "assets/css/style.css",
        "assets/css/headers/header-v6.css",
        "assets/css/footers/footer-v2.css",
        "assets/css/colors.css",
        "assets/css/custom.css",
    ],
    comboFile: 'main.css',
    dest: dest + '/css',
    destDebug: dest + '/css-debug'

    // uncss parameters
    ignoreRules: [
        '.animated.flip',
        new RegExp('.header-v6(.header-dark-transparent)?.header-fixed-shrink'),
    ],
    htmlFiles = [
        'templates/new_homepage.html'
    ],
  }
};


gulp.task('compile-css-individual-debug', function () {
    return gulp.src(lodash.concat(config.css.bowerSourceFiles, config.css.assetsSourceFiles))
        .pipe(uncss({
            html: config.css.htmlFiles,
            ignore: config.css.ignoreRules,
        }))
        .pipe(rename({ extname: '.trim.css' }))
        .pipe(gulp.dest(config.css.destDebug))
        .pipe(cssnano({sourcemap: true}))
        .pipe(rename({ extname: '.min.css', }))
        .pipe(gulp.dest(config.css.destDebug));
});

gulp.task('compile-css-combined-bower', function () {
    return gulp.src(config.css.bowerSourceFiles)
        .pipe(sourcemaps.init())
          .pipe(concat('bower.css'))
        .pipe(sourcemaps.write())
        .pipe(gulp.dest(config.css.dest));
});

gulp.task('compile-css-combined-assets', function () {
    return gulp.src(config.css.assetsSourceFiles)
        .pipe(sourcemaps.init())
          .pipe(concat('assets.css'))
        .pipe(sourcemaps.write())
        .pipe(gulp.dest(config.css.dest));
});

gulp.task('compile-css-combined', ['compile-css-combined-bower', 'compile-css-combined-assets'], function () {

    return gulp.src([
            config.css.dest + '/bower.css',
            config.css.dest + '/assets.css'
        ])
        .pipe(sourcemaps.init({loadMaps: true}))
          .pipe(concat(config.css.comboFile))
          .pipe(gulp.dest(config.css.dest))
          .pipe(uncss({
              html: config.css.htmlFiles,
              ignore: config.css.ignoreRules,
          }))
          .pipe(rename({ extname: '.trim.css' }))
          .pipe(gulp.dest(config.css.dest))
          .pipe(cssnano())
          .pipe(rename({ extname: '.min.css', basename: path.basename(config.css.comboFile, '.css') }))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(config.css.dest));
});

gulp.task('compile-css', ['compile-css-individual-debug', 'compile-css-combined']);

gulp.task('compile-js', compileJavascript(false));
gulp.task('watchify', compileJavascript(true));

function compileJavascript(watch) {
  return function (callback) {
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

      // Allow us to use raw Bower modules
      b.transform(debowerify);
      // Convert JSX, if we see it
      b.transform(reactify);

      function buildBundle() {
        b.bundle()
          .pipe(source(file.dest))
          .pipe(buffer())

          .pipe(gulp.dest(config.javascript.dest))
          .pipe(sourcemaps.init({loadMaps: true}))
            .pipe(uglify())
            .on('error', gutil.log)
            .pipe(rename({ extname: '.min.js' }))
          .pipe(sourcemaps.write('.'))

          .pipe(gulp.dest(config.javascript.dest));
      }
      // On any dependency update, re-runs the bundler
      b.on('update', buildBundle);
      // And we need to run the builder once, to start things off.
      buildBundle();
    });

    callback();
  };
}

gulp.task('compile-images-resize', function () {
  gulp.src(baseAssetsDir + 'img/**/*.{png,jpg}')
    .pipe(responsive({
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
        width: 1600,
        quality: 60,
      }],
      'deets-head-and-title-on-black.png': [{
      }],
    }))
    .pipe(gulp.dest('dist/img'));
});

gulp.task('compile-images', ['compile-images-resize', 'compile-svg', 'compile-icons']);

// gets deets-activity svg files
gulp.task('compile-svg', function () {
  gulp.src(baseAssetsDir + 'img/*.svg')
    .pipe(gulp.dest('dist/img'));
});

gulp.task('compile-icons', function () {
  gulp.src('assets/img/icons/social/*.png')
    .pipe(gulp.dest('dist/img/icons/social/'));
});

gulp.task('compile-fonts', function () {
  gulp.src('bower_components/font-awesome/fonts/*.*')
    .pipe(gulp.dest('dist/fonts/'));
});

gulp.task('compile', ['compile-js', 'compile-css', 'compile-images', 'compile-fonts']);
