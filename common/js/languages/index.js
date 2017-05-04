/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import languages from './data';

const languageMap = {};
languages.forEach(x => {
  languageMap[x.iso] = x;
});
export default languageMap;
