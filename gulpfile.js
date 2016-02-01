var browserify = require('browserify');
var buffer     = require('vinyl-buffer');
var concatcss = require('gulp-concat-css');
var cssnano = require('gulp-cssnano');
var debowerify = require("debowerify");
var gulp = require('gulp');
var gutil = require('gutil');
var responsive = require('gulp-responsive-images');
var os = require("os");
var path = require('path');
var reactify   = require('reactify');
var rename = require('gulp-rename');
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
    source_files: [
        // url() will be relative to the first file I think,
        // so let's prioritize font-awesome since it references relative font files
        "bower_components/font-awesome/css/font-awesome.css",
        "bower_components/bootstrap/dist/css/bootstrap.css",
        "bower_components/animate.css/animate.css",
        "assets/css/style.css",
        "assets/css/app.css",
        "assets/css/headers/header-v6.css",
        "assets/css/footers/footer-v2.css",
        "assets/css/custom.css"
    ],
    combo_file: 'main.css',
    dest: dest + '/css',
    dest_debug: dest + '/css-debug'
  }
};


gulp.task('compile-css-individual-debug', function () {
    return gulp.src(config.css.source_files)
        .pipe(uncss({
            html: ['templates/new_homepage.html'],
            ignore: ['.animated.flip']
        }))
        .pipe(rename({ extname: '.trim.css' }))
        .pipe(gulp.dest(config.css.dest_debug))
        .pipe(cssnano())
        .pipe(rename({ extname: '.min.css', }))
        .pipe(gulp.dest(config.css.dest_debug));
});

gulp.task('compile-css-combined', function () {
    return gulp.src(config.css.source_files)
        .pipe(concatcss(config.css.combo_file))
        .pipe(gulp.dest(config.css.dest))
        .pipe(uncss({
            html: ['templates/new_homepage.html'],
            ignore: ['.animated.flip']
        }))
        .pipe(rename({ extname: '.trim.css' }))
        .pipe(gulp.dest(config.css.dest))
        .pipe(cssnano())
        .pipe(rename({ extname: '.min.css', basename: path.basename(config.css.combo_file, '.css') }))
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

// builds resized style/location jpg files
gulp.task('compile-images-style-location', function () {
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
gulp.task('compile-images-deets-activity', function () {
  gulp.src(baseAssetsDir + 'img/**/*.{png,jpg}')
    .pipe(responsive({
      'deets-activity-*.png': [{
        height: 100,
      }],
    }))
    .pipe(gulp.dest('dist/img'));
});

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

gulp.task('compile', ['compile-js', 'compile-css', 'compile-images-style-location', 'compile-images-deets-activity', 'compile-svg', 'compile-icons', 'compile-fonts']);
