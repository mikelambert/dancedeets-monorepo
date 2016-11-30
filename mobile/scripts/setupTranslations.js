#!/usr/bin/awk BEGIN{a=b=ARGV[1];sub(/[A-Za-z_.]+$/,"runNode.js",a);sub(/^.*\//,"./",b);system(a"\t"b)}

/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */


import * as path from 'path';
import * as fs from 'fs';
import stableJsonStringify from 'json-stable-stringify';
import {
  walk,
  writeFile,
} from './_fsPromises';

function generateJsonFile(translations) {
  return stableJsonStringify(translations, { space: 2 });
}

const locales = ['en', 'fr', 'ja', 'zh'];

function loadJsonFile(filename) {
  return JSON.parse(fs.readFileSync(filename, 'utf8'));
}

async function updateWithTranslations(englishTranslation) {
  const promises = locales.map((locale) => {
    const filename = path.resolve(`./js/messages/${locale}.json`);
    const localeTranslation = locale === 'en' ? {} : loadJsonFile(filename);
    Object.keys(englishTranslation).forEach((key) => {
      if (!localeTranslation[key]) {
        localeTranslation[key] = englishTranslation[key];
      }
    });
    console.log('Writing ', filename);
    return writeFile(filename, generateJsonFile(localeTranslation));
  });
  // Write out all files
  await Promise.all(promises);
}

async function run() {
  const filenames = await walk('build/messages');
  // $FlowFixMe: This is a dev script, and so can use dynamic includes
  const jsons = filenames.map(file => require(file));
  const json = jsons.reduce((result, jsList) => result.concat(jsList), []);
  const translationLookup = {};
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
