/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import * as fs from 'fs';
import * as path from 'path';
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
  // TODO: do we want to write out js files or json files?
  // return stableJsonStringify(translations, {space: 2});
  let data = `/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

export default 
`;
  data += stableJsonStringify(translations, {space: 2});
  data += ';\n';
  return data;
}

const locales = ['fr', 'ja', 'zh'];


async function updateWithTranslations(englishTranslation) {
  const data = generateFile(englishTranslation);
  await writeFile(path.resolve('./js/messages/en.js'), data);

  const promises = locales.map((locale) => {
    const filename = path.resolve(`./js/messages/${locale}.js`);
    // TODO: For some reason, this fails to load anything, and causes the problem to abort
    const localeTranslation = require(filename);
    Object.keys(englishTranslation).forEach((key) => {
      if (!localeTranslation[key]) {
        localeTranslation[key] = englishTranslation[key];
      }
    });
    return writeFile(filename, generateFile(localeTranslation));
  });
  // Write out all files
  await Promise.all(promises);
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
  await updateWithTranslations(translationLookup);
}

try {
  run();
} catch (e) {
  console.warn(e);
}
