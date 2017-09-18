/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

// This gulpfile makes use of new JavaScript features.
// Babel handles this without us having to do anything. It just works.
// You can read more about the new JavaScript features here:
// https://babeljs.io/docs/learn-es2015/

import fs from 'fs';
import glob from 'glob';
import gulp from 'gulp';
import gulpLoadPlugins from 'gulp-load-plugins';
import runSequence from 'run-sequence';
import yaml from 'js-yaml';
import taskListing from 'gulp-task-listing';
import { execSync } from 'child_process';
import flatten from 'lodash/flatten';
import yargs from 'yargs';

const argv = yargs
  .option('a', {
    alias: 'a',
    description: 'The params to pass to scrapers',
    default: '',
  })
  .help('h')
  .alias('h', 'help')
  .strict().argv;

gulp.task('help', taskListing);
gulp.task('default', taskListing);

const $ = gulpLoadPlugins();

function getScrapyNames(pattern) {
  return glob
    .sync(pattern)
    .map(filename => {
      const contents = fs.readFileSync(filename, 'utf8');
      const match = contents.match(/name = ['"](.*)['"]/);
      if (match) {
        return match[1];
      } else {
        return null;
      }
    })
    .filter(x => x);
}

const allSpiderModules = execSync('python scrapy_settings.py');
const allSpiderFiles = allSpiderModules
  .toString()
  .trim()
  .toString()
  .split('\n')
  .map(x => `${x.replace('.', '/')}/*.py`)
  .map(getScrapyNames);

flatten(allSpiderFiles).forEach(x =>
  gulp.task(
    `scrape:one:${x}`,
    $.shell.task(`./scrapy_bin.py crawl ${x} -a ${argv.a}`)
  )
);
gulp.task(
  'scrape:classes:index:prod',
  $.shell.task(['curl https://www.dancedeets.com/classes/reindex'])
);
gulp.task(
  'scrape:classes:index:dev',
  $.shell.task(['curl http://dev.dancedeets.com:8080/classes/reindex'])
);
gulp.task('scrape:web', ['scrape:web:scrapy']);
gulp.task('scrape:classes', cb =>
  runSequence(
    'scrape:classes:scrapy',
    ['scrape:classes:index:prod', 'scrape:classes:index:dev'],
    cb
  )
);
gulp.task('scrapeWeb', ['scrape:web']);
gulp.task('scrapeClasses', ['scrape:classes']);

function getScrapyKey() {
  if (!fs.existsSync('keys.yaml')) {
    return 'NO KEY';
  }
  const yamlDoc = yaml.safeLoad(fs.readFileSync('keys.yaml', 'utf8'));
  return yamlDoc.scrapinghub_key;
}

gulp.task(
  'deploy:scrapy',
  $.shell.task([
    `echo ${getScrapyKey()} | PYTHONPATH=lib-local:. shub login`,
    'PYTHONPATH=lib-local:. shub deploy',
  ])
);
