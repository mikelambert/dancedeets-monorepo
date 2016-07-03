/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import * as fs from 'fs';
import * as path from 'path';
import * as glob from 'glob';
import clone from 'git-clone';
import {sync as mkdirpSync} from 'mkdirp';
import stableJsonStringify from 'json-stable-stringify';

function walk(dir) {
  var results = [];
  return new Promise((resolve, reject) => {
    fs.readdir(dir, function(err, list) {
      if (err) {
        return reject(err);
      }
      var pending = list.length;
      if (!pending) {
        return resolve(results);
      }
      list.forEach(function(file) {
        file = path.resolve(dir, file);
        fs.stat(file, function(err2, stat) {
          if (stat && stat.isDirectory()) {
            walk(file).then(function(res) {
              results = results.concat(res);
              if (!--pending) {
                resolve(results);
              }
            });
          } else {
            results.push(file);
            if (!--pending) {
              resolve(results);
            }
          }
        });
      });
    });
  });
}

function writeFile(filename, contents) {
  return new Promise((resolve, reject) => {
    console.log(filename);
    fs.writeFile(filename, contents, (err) => {
      if (err) {
        reject(err);
      } else {
        resolve(path.resolve(filename));
      }
    });
  });
}

function generateFile(translations) {
  let data = `/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

export default 
`;
  data += stableJsonStringify(translations, {space: 2});
  return data;
}

async function run() {
  const filenames = await walk('build/messages');
  const jsons = filenames.map((file) => require(file));
  const json = jsons.reduce((result, jsList) => {
    result = result.concat(jsList);
    return result;
  }, []);
  var translationLookup = {};
  json.forEach((x) => {
    translationLookup[x.id] = x.defaultMessage;
  });
  const data = generateFile(translationLookup);
  console.log(data);
  await writeFile('js/messages/en.js', data);
}

run().then(() => null);
/*
function(err, results) {
  if (err) {
    throw err;
  }
  console.log(results);
});
*/


const REPO_PATH = 'build/country-list';

const locales = ['en', 'fr', 'zh_Hans', 'zh_Hant', 'ja', 'de', 'it', 'nl', 'ru', 'ko', 'es'];

function downloadCountryList(cb) {
  mkdirpSync('build');
  clone('https://github.com/umpirsky/country-list.git', REPO_PATH, {shallow: true}, cb);
}

function getLocaleFrom(filename) {
  const components = filename.split('/');
  return components[components.length - 2];
}

function combineCountryList(filter, cb) {
  const combined = glob.sync(`${REPO_PATH}/data/*/country.json`)
    .filter((filename) => {
      const locale = getLocaleFrom(filename);
      return filter(locale);
    })
    .reduce((reduced, filename) => {
      const locale = getLocaleFrom(filename);
      const data = require(`../${filename}`);
      reduced[locale] = data;
      return reduced;
    }, {});

  cb(combined);
}

function languageFilter(locale) {
  return locales.indexOf(locale) !== -1;
}

function saveCombinedList(combined) {
  let fileData = 'export default ';
  fileData += JSON.stringify(combined);
  mkdirpSync('js/data');
  writeFile('js/data/localizedCountries.js', fileData).then(() => null);
}
