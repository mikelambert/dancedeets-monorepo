/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import Firestack from 'react-native-firestack';

const configurationOptions = {
  debug: true,
};
const firestack = new Firestack(configurationOptions);
firestack.on('debug', msg => console.log('Received debug message', msg));
firestack.database.setPersistence(true);

export default firestack;
