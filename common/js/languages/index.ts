/**
 * Copyright 2016 DanceDeets.
 */

import languages from './data';

interface Language {
  iso: string;
  [key: string]: unknown;
}

const languageMap: Record<string, Language> = {};
languages.forEach((x: Language) => {
  languageMap[x.iso] = x;
});
export default languageMap;
