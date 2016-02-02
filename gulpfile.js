var browserify = require('browserify');
var buffer     = require('vinyl-buffer');
var concat = require('gulp-concat');
var cssnano = require('gulp-cssnano');
var debowerify = require("debowerify");
var del = require('del');
var gulp = require('gulp');
var gulpif = require('gulp-if');
var gutil = require('gutil');
var lodash = require('lodash')
var os = require("os");
var path = require('path');
var reactify   = require('reactify');
var rename = require('gulp-rename');
var responsive = require('gulp-responsive-images');
var runSequence = require('run-sequence');
var sass = require('gulp-sass');
var shell = require('gulp-shell');
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
    sourceFiles: [
        "bower_components/font-awesome/css/font-awesome.css",
        "bower_components/bootstrap/dist/css/bootstrap.css",
        "bower_components/animate.css/animate.css",
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

function compileCssTo(destDir, destFilename) {
    return function() {
        return gulp.src(lodash.concat(config.css.sourceFiles))
            .pipe(sourcemaps.init({loadMaps: true}))
                .pipe(gulpif('*.{sass,scss}', sass().on('error', sass.logError)))
                .pipe(gulpif(destFilename != null, concat(destFilename || 'dummyArgSoConstructorPasses')))
                .pipe(gulp.dest(destDir))
                .pipe(uncss(config.css.uncssArgs))
                .pipe(rename({ extname: '.trim.css' }))
                .pipe(gulp.dest(destDir))
                .pipe(cssnano({sourcemap: true}))
                .pipe(rename({ extname: '.min.css', basename: path.basename(config.css.comboFile, '.css') }))
                .pipe(gulp.dest(destDir))
            .pipe(sourcemaps.write('.'));
    }
}

gulp.task('compile-css', compileCssTo(config.css.destDebug, 'main.css'));
gulp.task('compile-css-individual-debug', compileCssTo(config.css.destDebug));

gulp.task('compile-js', compileJavascript(false));
gulp.task('watchify', compileJavascript(true));

gulp.task('sass', function () {
    gulp.src('./sass/**/*.scss')
       .pipe(sass({outputStyle: 'compressed'}))
       .pipe(gulp.dest('./css'));
});

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
        return b.bundle()
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
      return buildBundle();
    });

    callback();
  };
}

gulp.task('compile-images-resize', function () {
  return gulp.src(baseAssetsDir + 'img/**/*.{png,jpg}')
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
  return gulp.src(baseAssetsDir + 'img/*.svg')
    .pipe(gulp.dest('dist/img'));
});

gulp.task('compile-icons', function () {
  return gulp.src('assets/img/icons/social/*.png')
    .pipe(gulp.dest('dist/img/icons/social/'));
});

gulp.task('compile-fonts', function () {
  return gulp.src('bower_components/font-awesome/fonts/*.*')
    .pipe(gulp.dest('dist/fonts/'));
});

gulp.task('compile', ['compile-js', 'compile-css', 'compile-images', 'compile-fonts']);

gulp.task('clean', function() {
  return del.sync('dist');
})

gulp.task('test', shell.task(['./nose.sh']));

gulp.task('clean-build-test', function (callback) {
    runSequence('clean', 'compile', 'test', callback);
});

gulp.task('deploy', ['clean-build-test'], shell.task(['./deploy.sh']));