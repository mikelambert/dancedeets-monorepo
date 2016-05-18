import React from 'react';
import { GooglePlacesAutocomplete } from './GooglePlacesAutocomplete';
import { defaultFont } from './DDText';

const locations = [
  {description: 'New York City', geometry: { location: { lat: 40.7058254, lng: -74.1180861 } }},
  {description: 'Los Angeles', geometry: { location: { lat: 34.0207504, lng: -118.691914 } }},
  {description: 'Paris', geometry: { location: { lat: 48.8589101, lng: 2.3125376 } }},
  {description: 'Tokyo', geometry: { location: { lat: 35.6735408, lng: 139.5703049 } }},
  {description: 'Osaka', geometry: { location: { lat: 34.678434, lng: 135.4776404 } }},
  {description: 'Taipei', geometry: { location: { lat: 25.0855451, lng: 121.4932093 } }},
];

export default class Autocomplete extends React.Component {
  render() {
    return (
      <GooglePlacesAutocomplete
        placeholder="Location"
        minLength={2} // minimum length of text to search
        autoFocus={false}
        fetchDetails={true}
        onPress={(data, details = null) => { // 'details' is provided when fetchDetails = true
          console.log(data);
          console.log(details);
        }}
        getDefaultValue={() => {
          return ''; // text input default value
        }}
        query={{
          // available options: https://developers.google.com/places/web-service/autocomplete
          key: 'AIzaSyDEHGAeT9NkW-CvcaDMLbz4B6-abdvPi4I',
          language: 'en', // language of the results
          types: '(regions)', // default: 'geocode'
        }}
        styles={{
          textInputContainer: {
            backgroundColor: 'black',
            borderTopWidth: 0,
            borderBottomWidth: 0,
            height: null,
          },
          description: {
            color: 'white',
          },
          predefinedPlacesDescription: {
            color: 'white',
          },
          textInput: Object.assign({
            borderRadius: 5,
            height: 30,
            flex: 1,
            marginTop: 3,
            marginBottom: 3,
            marginLeft: 3,
            marginRight: 3,
            paddingTop: 0,
            paddingBottom: 0,
            paddingLeft: 0,
            paddingRight: 0,
            padding: 0,
            fontSize: null,
            backgroundColor: 'rgba(255, 255, 255, 0.25)',
          }, defaultFont),
          listView: {
            //position: 'absolute',
            backgroundColor: 'black',
          },
        }}

        placeholder="Location"
        returnKeyType="search"
        textInputProps={{
          placeholderTextColor: 'rgba(255, 255, 255, 0.5)',
          keyboardAppearance: 'dark',
          selectTextOnFocus: true,
          autoCorrect: false,
          autoCapitalize: 'none',
        }}

        currentLocation={true} // Will add a 'Current location' button at the top of the predefined places list
        currentLocationLabel="Current Location"
        nearbyPlacesAPI="GoogleReverseGeocoding" // Which API to use: GoogleReverseGeocoding or GooglePlacesSearch
        filterReverseGeocodingByTypes={['political', 'administrative_area_level_3']}
        GoogleReverseGeocodingQuery={{
          // available options for GoogleReverseGeocoding API : https://developers.google.com/maps/documentation/geocoding/intro
        }}
        GooglePlacesSearchQuery={{
          // available options for GooglePlacesSearch API : https://developers.google.com/places/web-service/search
        }}


        filterReverseGeocodingByTypes={['locality', 'administrative_area_level_3']} // filter the reverse geocoding results by types - ['locality', 'administrative_area_level_3'] if you want to display only cities

        predefinedPlaces={locations}
        enablePoweredByContainer={false}
        { ...this.props }
      />
    );
  }
}
