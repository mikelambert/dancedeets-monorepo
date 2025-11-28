/**
 * Copyright 2016 DanceDeets.
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

function generateArgString(args: Record<string, any>): string {
  const argsString = Object.keys(args)
    .map(key => `--${key}=${String(args[key])}`)
    .join(' ');
  return argsString;
}

function remoteJob(name: string, module: string, args: Record<string, any>) {
  // args.run_on_fraction = true;
  const jobName = name.toLowerCase().replace(/[^-a-z0-9]/, '-');
  const argsString = generateArgString(args);
  const command = `/usr/bin/python -m ${module} --log=DEBUG --project dancedeets-hrd --job_name=${jobName} --runner DataflowRunner --staging_location ${bucket}/staging --temp_location ${bucket}/temp --output ${bucket}/output --setup_file ./setup.py --num_workers 50 ${argsString}`;
  return $.shell.task([command]);
}

function localJob(name: string, module: string, args: Record<string, any>) {
  const argsString = generateArgString(args);
  return $.shell.task([
    `/usr/bin/python -m ${module} --log=DEBUG --run_locally=true ${argsString}`,
  ]);
}

function localRemoteTasks(name: string, module: string, args: Record<string, any> = {}) {
  gulp.task(`${name}:remote`, remoteJob(name, module, args));
  gulp.task(`${name}:local`, localJob(name, module, args));
}

localRemoteTasks('pr-city-category', 'popular_people', {
  ground_truth_events: true,
  want_top_attendees: true,
});
localRemoteTasks('pr-debug-attendees', 'popular_people', {
  ground_truth_events: true,
  debug_attendees: true,
});
localRemoteTasks('pr-person-city', 'popular_people', {
  ground_truth_events: false,
  person_locations: true,
});
localRemoteTasks('delete_old', 'delete_old');

gulp.task('popular_people:complete', cb =>
  runSequence(
    'popular_people:remote',
    'popular_people:download',
    'popular_people:upload',
    cb
  )
);
