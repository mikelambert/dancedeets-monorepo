/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import languages from './languages.json';
const languageMap = {};
languages.forEach((x) => {
  languageMap[x.iso] = x;
});
export default languageMap;
