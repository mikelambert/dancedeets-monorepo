/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import languages from './languagesData.json';
const languageMap = {};
languages.forEach((x) => {
  languageMap[x.iso] = x;
});
export default languageMap;
