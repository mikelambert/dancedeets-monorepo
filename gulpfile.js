var browserify = require('browserify');
var buffer     = require('vinyl-buffer');
var changed = require("gulp-changed");
var debowerify = require("debowerify");
var gulp = require('gulp');
var responsive = require('gulp-responsive-images');
var os = require("os");
var sourcemaps = require('gulp-sourcemaps');
var reactify   = require('reactify');
var source     = require('vinyl-source-stream');
var uglify = require('gulp-uglify');
const username = require('username')


var baseAssetsDir = '/Users/' + username.sync() + '/Dropbox/dancedeets-art/build-assets/'


var src  = './';
var dest = './dist';
var config = {
  javascript: {
    src: src + '/javascript_app/**/*.{js,coffee}',
    rootFiles: [
      {
        src  : src + '/main.js',
        dest : 'main.js'
      },
    ],
    dest: dest + '/js'
  }
};

function mapName(dir, jsName) {

}

gulp.task('browserify', function (callback) {
  var files = config.javascript.rootFiles;
  
  files.forEach(function (file) {
    var b = browserify({
        entries: file.src, // Only need initial file, browserify finds the deps
        debug: true        // Enable sourcemaps
    });

    b.transform(debowerify);
    b.transform(reactify);  // Convert JSX

    b.bundle()
      .pipe(source(file.dest))
      .pipe(buffer())

      .pipe(sourcemaps.init({loadMaps: true}))
        .pipe(uglify())
      .pipe(sourcemaps.write('.'))

      .pipe(gulp.dest(config.javascript.dest));
  });

  callback();
});

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
