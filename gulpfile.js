var browserify = require('browserify');
var buffer     = require('vinyl-buffer');
var concatcss = require('gulp-concat-css');
var cssnano = require('gulp-cssnano');
var debowerify = require("debowerify");
var gulp = require('gulp');
var gutil = require('gutil');
var responsive = require('gulp-responsive-images');
var os = require("os");
var reactify   = require('reactify');
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
    src: src + '/javascript_app/**/*.{js,jsx}',
    rootFiles: [
      {
        src  : src + '/main.js',
        dest : 'main.js'
      },
    ],
    dest: dest + '/js'
  },
  css: {
    src: src + '/javascript_app/**/*.{js,jsx}',
    rootFiles: [
      {
        src  : src + '/main.js',
        dest : 'main.css'
      },
    ],
    dest: dest + '/css'
  }
};

var css_files = [
    "bower_components/bootstrap/dist/css/bootstrap.css",
    "assets/css/style.css",
    "assets/css/ie8.css",
    "assets/css/blocks.css",
    "assets/css/plugins.css",
    "assets/css/app.css",
    "assets/css/one-theme.css",
    "assets/css/headers/header-v6.css",
    "assets/css/footers/footer-v2.css",
    "assets/css/theme-colors/default.css",
    "assets/css/theme-skins/dark.css",
    "bower_components/font-awesome/css/font-awesome.css",
    "bower_components/animate.css/animate.css",
    "assets/css/custom.css"
];

gulp.task('minify-css', function () {
    return gulp.src(css_files)
        .pipe(concatcss('main.css'))
        .pipe(uncss({
            html: ['templates/new_homepage.html'],
            ignore: ['.animated.flip']
        }))
        .pipe(cssnano())
        .pipe(gulp.dest('dist/css'));
});

gulp.task('browserify', compileJavascript(false));
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

          .pipe(sourcemaps.init({loadMaps: true}))
            .pipe(uglify())
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

// builds resized style/location jpg files
gulp.task('resize-style-location', function () {
  gulp.src(baseAssetsDir + 'img/**/*.jpg')
    .pipe(responsive({
      '{location,style}-*.jpg': [{
        width: 450,
        height: 300,
        crop: 'true',
        quality: 60,
      }],
    }))
    .pipe(gulp.dest('dist/img'));
});

// builds resized deets-activity png files
gulp.task('resize-deets', function () {
  gulp.src(baseAssetsDir + 'img/**/*.{png,jpg}')
    .pipe(responsive({
      'deets-activity-*.png': [{
        width: 100,
      }],
    }))
    .pipe(gulp.dest('dist/img'));
});

// gets deets-activity svg files
gulp.task('copy-svg', function () {
  gulp.src(baseAssetsDir + 'img/*.svg')
    .pipe(gulp.dest('dist/img'));
});

gulp.task('copy-icons', function () {
  gulp.src('assets/img/icons/social/*.png')
    .pipe(gulp.dest('dist/img/icons/social/'));
});

gulp.task('copy-fonts', function () {
  gulp.src('bower_components/font-awesome/fonts/*.*')
    .pipe(gulp.dest('dist/fonts/'));
});
