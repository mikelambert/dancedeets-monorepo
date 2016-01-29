var changed = require("gulp-changed");
var gulp = require('gulp');
var responsive = require('gulp-responsive-images');
var os = require("os");
const username = require('username')

var baseDir = '/Users/' + username.sync() + '/Dropbox/dancedeets-art/build-assets/'

// builds resized style/location jpg files
gulp.task('resize-style-location', function () {
  gulp.src(baseDir + 'img/**/*.jpg')
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
  gulp.src(baseDir + 'img/**/*.{png,jpg}')
    .pipe(responsive({
      'deets-activity-*.png': [{
        width: 100,
      }],
    }))
    .pipe(gulp.dest('dist/img'));
});

// gets deets-activity svg files
gulp.task('copy-svg', function () {
  gulp.src(baseDir + 'img/*.svg')
    .pipe(gulp.dest('dist/img'));
});
