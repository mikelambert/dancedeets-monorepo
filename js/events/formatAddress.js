/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */


export type Address = {
  position: {
    lat: number;
    lng: number;
  };
  locale: string;

  thoroughfare: string;
  subThoroughfare: string;

  subLocality: string;
  locality: string;
  postalCode: string;

  // Why do we sometimes get one or the other?! :(
  subAdminArea: string;
  subAdministrativeArea: string;
  // Why do we sometimes get one or the other?! :(
  adminArea: string;
  administrativeArea: string;

  country: string;
  countryCode: string;
};

/*
// Uses subAdministrativeArea
{
  "postalCode":"10024",
  "subAdministrativeArea":"New York",
  "name":"Central Park",
  "locality":"New York",
  "subThoroughfare":"1000",
  "administrativeArea":"NY",
  "position":{
    "lat":40.7964708,
    "lng":-73.9545696
  },
  "country":"United States",
  "subLocality":"Manhattan",
  "thoroughfare":"5th Ave"
}

// Uses subAdminArea, has formattedAddress
{
  adminArea: "CA"
  country: "United States"
  countryCode: "US"
  feature: null
  formattedAddress: "I-280 N,Los Altos, CA  94022,United States"
  locality: "Los Altos Hills"
  position: Object
  postalCode: "94022",
  streetName: "I-280 N",
  streetNumber: null.
  subAdminArea: "Santa Clara",
  subLocality: null,
}
*/


export function format(address: Address) {
  var components = [];
  // We really need *something* smaller than the AdminArea/State level.
  // Especially since there might not be a State sometimes (ie Helsinki, Finland).
  if (address.locality != null) {
      // Sometimes there is only a Locality:
      // LatLong=35.6583942,139.6990928
      // SubLocality=null
      // Locality=Shibuya
      // SubAdminArea=null
      // AdminArea=Tokyo
      //
      // Los Altos Hills, CA (ignores Santa Clara County in subadminarea)
      components.push(address.locality);
  } else if (address.subAdminArea != null) {
      components.push(address.subAdminArea);
  } else if (address.subAdministrativeArea != null) {
      // Sometimes there is only a SubAdminArea:
      // LatLong=60.1836354,24.9206748
      // SubLocality=null
      // Locality=null
      // SubAdminArea=Helsinki
      // AdminArea=null
      components.push(address.subAdministrativeArea);
  } else if (address.subLocality != null) {
      // Sometimes there is only a SubLocality:
      // LatLong=40.790278,-73.959722
      // SubLocality=Dundas
      // Locality=null
      // SubAdminArea=null
      // AdminArea=Ontario
      // Dundas appears to be the smallest unit of geography,
      // so we check for it in the third if-block, hoping to find a proper city first.
      components.push(address.subLocality);
  }
  // Sometimes there is too much data, and we want to drop a lot of it:
  // LatLong=40.790278,-73.959722
  // SubLocality=Manhattan
  // Locality=New York (the city)
  // SubAdminArea=New York (the county)
  // AdminArea=New York (the state)
  // In this case, we just want to grab the Locality (first if-block above)

  // Then grab the States/Province/etc (for those who have it)
  if (address.adminArea != null) {
      components.push(address.adminArea);
  }
  if (address.administrativeArea != null) {
      components.push(address.administrativeArea);
  }
  // And finally the Country, which should always be there...unless....I'm on a boat!
  // So let's be safe and make this optional, in which case we basically take whatever we can get
  if (address.country != null) {
      components.push(address.country);
  }
  return components.join(', ');
}
