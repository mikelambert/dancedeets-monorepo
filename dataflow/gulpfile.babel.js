
// This gulpfile makes use of new JavaScript features.
// Babel handles this without us having to do anything. It just works.
// You can read more about the new JavaScript features here:
// https://babeljs.io/docs/learn-es2015/

import gulp from 'gulp';
import gulpLoadPlugins from 'gulp-load-plugins';
import taskListing from 'gulp-task-listing';

gulp.task('help', taskListing);
gulp.task('default', taskListing);

const $ = gulpLoadPlugins();

gulp.task('prepare', $.shell.task([
  'pip install googledatastore google-apitools "git+https://github.com/apache/beam.git#egg=0.7.0-dev&subdirectory=sdks/python" -t lib',
  'pip install google-cloud-datastore --user',
  'wget https://github.com/apache/beam/archive/master.zip',
  'unzip master.zip',
  'cd beam-master/sdks/python/',
  'python setup.py sdist',
  'cd ../../..',
]))

const sdk = 'beam-master/sdks/python/dist/apache-beam-0.7.0.dev0.tar.gz';
const bucket = 'gs://dancedeets-hrd.appspot.com';

function remoteJob(filename) {
  return $.shell.task([`/usr/local/bin/python -m ${filename} --log=DEBUG --project dancedeets-hrd --job-name=${filename} --runner DataflowRunner --staging_location ${bucket}/staging --temp_location ${bucket}/temp --output ${bucket}/output --sdk_location ${sdk} --setup_file ./setup.py --num_workers=400`]);
}

function localJob(filename) {
  return $.shell.task([`/usr/local/bin/python -m ${filename} --log=DEBUG --run_locally=true`]);
}

function localRemoteTasks(command) {
  gulp.task(`${command}:remote`, remoteJob(command));
  gulp.task(`${command}:local`, localJob(command));
}

localRemoteTasks('popular_people');
localRemoteTasks('delete_old');

