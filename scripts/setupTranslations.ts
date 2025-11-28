#!/usr/bin/awk BEGIN{a=b=ARGV[1];sub(/[A-Za-z_.]+$/,"../runNode.js",a);sub(/^.*\//,"./",b);system(a"\t"b)}

/**
 * Copyright 2016 DanceDeets.
 */

import * as path from 'path';
import stableJsonStringify from 'json-stable-stringify';
import fs from 'fs-extra';

interface Translation {
  [key: string]: string;
}

function generateJsonFile(translations: Translation): string {
  return stableJsonStringify(translations, { space: 2 });
}

const locales = ['en', 'fr', 'ja', 'zh'];

function loadJsonFile(filename: string): Translation {
  return JSON.parse(fs.readFileSync(filename, 'utf8'));
}

interface MessageEntry {
  id: string;
  defaultMessage: string;
}

async function updateWithTranslations(englishTranslation: Translation): Promise<void> {
  const promises = locales.map(locale => {
    const filename = path.resolve(`../common/js/messages/${locale}.json`);
    const localeTranslation: Translation = locale === 'en' ? {} : loadJsonFile(filename);
    Object.keys(englishTranslation).forEach(key => {
      if (!localeTranslation[key]) {
        localeTranslation[key] = englishTranslation[key];
      }
    });
    console.log('Writing ', filename);
    return fs.writeFile(filename, generateJsonFile(localeTranslation));
  });
  // Write out all files
  await Promise.all(promises);
}

async function run(): Promise<void> {
  const filenames: string[] = (fs as any).walkSync('../build/messages');
  // @ts-ignore: This is a dev script, and so can use dynamic includes
  const jsons: MessageEntry[][] = filenames.map((file: string) => require(file));
  const json = jsons.reduce((result, jsList) => result.concat(jsList), []);
  const translationLookup: Translation = {};
  json.forEach(x => {
    translationLookup[x.id] = x.defaultMessage;
  });
  await updateWithTranslations(translationLookup);
}

run();
