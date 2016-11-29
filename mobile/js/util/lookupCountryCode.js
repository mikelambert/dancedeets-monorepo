/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import localizedCountries from '../data/localizedCountries';

// localizedCountries is a {languageCode: {countryCode: countryName}} object
// Let's convert that to an easy lookup: {countryName: countryCode}
const countryLookup = Object.keys(localizedCountries).reduce((reduction, languageCode) => {
  Object.keys(localizedCountries[languageCode]).reduce((reduction2, countryCode) => {
    const country = localizedCountries[languageCode][countryCode];
    reduction2[country] = countryCode;
    return reduction2;
  }, reduction);
  return reduction;
}, {});
// Some manual fixups
countryLookup['Hong Kong'] = 'HK';
countryLookup['香港'] = 'HK';

export default function(country: string) {
  return countryLookup[country];
}
