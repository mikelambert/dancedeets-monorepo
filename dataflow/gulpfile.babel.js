/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

// This gulpfile makes use of new JavaScript features.
// Babel handles this without us having to do anything. It just works.
// You can read more about the new JavaScript features here:
// https://babeljs.io/docs/learn-es2015/

import gulp from 'gulp';
import gulpLoadPlugins from 'gulp-load-plugins';
import taskListing from 'gulp-task-listing';
import runSequence from 'run-sequence';

gulp.task('help', taskListing);
gulp.task('default', taskListing);

const $ = gulpLoadPlugins();

const bucket = 'gs://dancedeets-hrd.appspot.com';

function remoteJob(filename) {
  const jobName = filename.replace(/[^-a-z0-9]/, '-');
  return $.shell.task([
    `/usr/local/bin/python -m ${filename} --log=DEBUG --project dancedeets-hrd --job_name=${jobName} --runner DataflowRunner --staging_location ${bucket}/staging --temp_location ${bucket}/temp --output ${bucket}/output --setup_file ./setup.py --num_workers 100`,
  ]);
}

function localJob(filename) {
  return $.shell.task([
    `/usr/local/bin/python -m ${filename} --log=DEBUG --run_locally=true`,
  ]);
}

function localRemoteTasks(command) {
  gulp.task(`${command}:remote`, remoteJob(command));
  gulp.task(`${command}:local`, localJob(command));
}

localRemoteTasks('popular_people');
localRemoteTasks('delete_old');

gulp.task(
  'popular_people:download',
  $.shell.task(['cd ../server && python tools/download_pr_data.py'])
);

gulp.task('popular_people:upload', $.shell.task(['./tools/upload_pr_data.sh']));

gulp.task('popular_people:complete', cb =>
  runSequence(
    'popular_people:remote',
    'popular_people:download',
    'popular_people:upload',
    cb
  )
);
