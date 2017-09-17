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

const webEventNames = getScrapyNames('web_events/scraper/spiders/*.py');
const classesNames = getScrapyNames('classes/scraper/spiders/*.py');

webEventNames
  .concat(classesNames)
  .forEach(x =>
    gulp.task(`scrape:one:${x}`, $.shell.task(`./scrapy_bin.py crawl ${x}`))
  );
gulp.task('scrape:web:scrapy', webEventNames.map(x => `scrape:one:${x}`));
gulp.task('scrape:classes:scrapy', classesNames.map(x => `scrape:one:${x}`));
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
