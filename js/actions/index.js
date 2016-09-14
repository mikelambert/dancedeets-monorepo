/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import * as addEvents from './addEvents';
import * as login from './login';
import * as mainTabs from './mainTabs';
import * as navigation from './navigation';
import * as search from './search';
import * as translate from './translate';

module.exports = {
  ...addEvents,
  ...login,
  ...mainTabs,
  ...navigation,
  ...search,
  ...translate,
};
