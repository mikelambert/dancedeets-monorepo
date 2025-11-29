#!/usr/bin/awk BEGIN{a=b=ARGV[1];sub(/[A-Za-z_.]+$/,"../../runNode.js",a);sub(/^.*\//,"./",b);system(a"\t"b)}

/**
 * Copyright 2016 DanceDeets.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as glob from 'glob';
import clone from 'git-clone';
import { sync as mkdirpSync } from 'mkdirp';

function writeFile(filename: string, contents: string): Promise<string> {
  return new Promise((resolve, reject) => {
    fs.writeFile(filename, contents, err => {
      if (err) {
        reject(err);
      } else {
        resolve(path.resolve(filename));
      }
    });
  });
}

const REPO_PATH = 'build/country-list';

const locales = [
  'en',
  'fr',
  'zh_Hans',
  'zh_Hant',
  'ja',
  'de',
  'it',
  'nl',
  'ru',
  'ko',
  'es',
];

function downloadCountryList(cb: (err?: Error) => void): void {
  mkdirpSync('build');
  clone(
    'https://github.com/umpirsky/country-list.git',
    REPO_PATH,
    { shallow: true },
    cb
  );
}

function getLocaleFrom(filename: string): string {
  const components = filename.split('/');
  return components[components.length - 2];
}

function combineCountryList(
  filter: (locale: string) => boolean,
  cb: (combined: Record<string, Record<string, string>>) => void
): void {
  const combined = glob
    .sync(`${REPO_PATH}/data/*/country.json`)
    .filter(filename => {
      const locale = getLocaleFrom(filename);
      return filter(locale);
    })
    .reduce((reduced: Record<string, Record<string, string>>, filename) => {
      const locale = getLocaleFrom(filename);
      // @ts-ignore: This is a dev script, and so can use dynamic includes
      const data = require(`../${filename}`);
      reduced[locale] = data;
      return reduced;
    }, {});

  cb(combined);
}

function languageFilter(locale: string): boolean {
  return locales.indexOf(locale) !== -1;
}

function saveCombinedList(combined: Record<string, Record<string, string>>): void {
  let fileData = 'export default ';
  fileData += JSON.stringify(combined);
  mkdirpSync('js/data');
  writeFile('js/data/localizedCountries.js', fileData).then(() => null);
}

downloadCountryList(() => combineCountryList(languageFilter, saveCombinedList));
