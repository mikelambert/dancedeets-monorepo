/**
 * Copyright 2016 DanceDeets.
 * Modified from react-native-google-places-autocomplete.
 * @flow
 */

import React from 'react';
import {TextInput, View, ListView, Image, TouchableHighlight, Platform, ActivityIndicatorIOS, ProgressBarAndroid} from 'react-native';
import {Text} from './DDText';
import Qs from 'qs';

const defaultStyles = {
  textInput: {
  },
  listView: {
    position: 'absolute',
    // flex: 1,
  },
  row: {
    padding: 13,
    height: 44,
    flexDirection: 'row',
  },
  separator: {
    height: 1,
    backgroundColor: '#c8c7cc',
  },
  description: {
  },
  loader: {
    // flex: 1,
    flexDirection: 'row',
    justifyContent: 'flex-end',
    height: 20,
  },
  androidLoader: {
    marginRight: -15,
  },
};

type Result = {
  description?: string;
  formatted_address?: string;
  name?: string;
  isCurrentLocation?: boolean;
  isLoading?: boolean;
  isPredefinedPlace?: boolean;
  place_id?: string;
};

class AutocompleteList extends React.Component {

};

export class GooglePlacesAutocomplete extends React.Component {
  state: {
    text: string,
    dataSource: ListView.DataSource,
    listViewDisplayed: boolean,
  };

  _results: [Result] = [];
  _requests: [XMLHttpRequest] = [];


  props: {
    placeholder: string,
    onPress: () => void,
    minLength: number,
    fetchDetails: boolean,
    autoFocus: boolean,
    getDefaultValue: () => string,
    timeout: number,
    onTimeout: () => void,
    query: Object,
    GoogleReverseGeocodingQuery: Object,
    GooglePlacesSearchQuery: Object,
    styles: Object,
    textInputProps: Object,
    predefinedPlaces: [Result],
    currentLocation: boolean,
    currentLocationLabel: string,
    nearbyPlacesAPI: string,
    filterReverseGeocodingByTypes: [string],
    predefinedPlacesAlwaysVisible: boolean,
  };

  static defaultProps = {
    placeholder: 'Search',
    onPress: () => {},
    minLength: 0,
    fetchDetails: false,
    autoFocus: false,
    getDefaultValue: () => '',
    timeout: 20000,
    onTimeout: () => console.warn('google places autocomplete: request timeout'),
    query: {
      key: 'missing api key',
      language: 'en',
      types: 'geocode',
    },
    GoogleReverseGeocodingQuery: {
    },
    GooglePlacesSearchQuery: {
      rankby: 'distance',
      types: 'food',
    },
    styles: {
    },
    textInputProps: {},
    predefinedPlaces: [],
    currentLocation: false,
    currentLocationLabel: 'Current location',
    nearbyPlacesAPI: 'GooglePlacesSearch',
    filterReverseGeocodingByTypes: [],
    predefinedPlacesAlwaysVisible: false,
  };

  constructor(props: any) {
    super(props);

    const ds = new ListView.DataSource({rowHasChanged: function rowHasChanged(r1, r2) {
      if (typeof r1.isLoading !== 'undefined') {
        return true;
      }
      return r1 !== r2;
    }});
    this.state = {
      text: this.props.getDefaultValue(),
      dataSource: ds.cloneWithRows(this.buildRowsFromResults([])),
      listViewDisplayed: false,
    };
    (this: any)._onFocus = this._onFocus.bind(this);
    (this: any)._onPress = this._onPress.bind(this);
    (this: any)._onChangeText = this._onChangeText.bind(this);
    (this: any)._renderRow = this._renderRow.bind(this);
  }

  buildRowsFromResults(results: [Result]): [Result] {
    var res: ?[Result] = null;

    if (results.length === 0 || this.props.predefinedPlacesAlwaysVisible === true) {
      res = [...this.props.predefinedPlaces];
      if (this.props.currentLocation === true) {
        res.unshift({
          description: this.props.currentLocationLabel,
          isCurrentLocation: true,
        });
      }
    } else {
      res = [];
    }

    res = res.map(function(place) {
      return {
        ...place,
        isPredefinedPlace: true,
      };
    });

    return [...res, ...results];
  }

  componentWillUnmount() {
    this._abortRequests();
  }

  _abortRequests() {
    for (let i = 0; i < this._requests.length; i++) {
      this._requests[i].abort();
    }
    this._requests = [];
  }

  /**
   * This method is exposed to parent components to focus on textInput manually.
   * @public
   */
  triggerFocus() {
    if (this.refs.textInput) {
      this.refs.textInput.focus();
    }
  }

  /**
   * This method is exposed to parent components to blur textInput manually.
   * @public
   */
  triggerBlur() {
    if (this.refs.textInput) {
      this.refs.textInput.blur();
    }
  }

  getCurrentLocation() {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        this._requestNearby(position.coords.latitude, position.coords.longitude);
      },
      (error) => {
        this._disableRowLoaders();
        alert(error.message);
      },
      {enableHighAccuracy: true, timeout: 20000, maximumAge: 1000}
    );
  }

  _enableRowLoader(rowData: Result) {

    let rows = this.buildRowsFromResults(this._results);
    for (let i = 0; i < rows.length; i++) {
      if ((rows[i].place_id === rowData.place_id) || (rows[i].isCurrentLocation === true && rowData.isCurrentLocation === true)) {
        rows[i].isLoading = true;
        this.setState({
          dataSource: this.state.dataSource.cloneWithRows(rows),
        });
        break;
      }
    }
  }

  _disableRowLoaders() {
    for (let i = 0; i < this._results.length; i++) {
      if (this._results[i].isLoading === true) {
        this._results[i].isLoading = false;
      }
    }
    this.setState({
      dataSource: this.state.dataSource.cloneWithRows(this.buildRowsFromResults(this._results)),
    });
  }

  _onPress(rowData: Result) {
    console.log("PRESSSSS!!!!!", rowData);
    if (rowData.isPredefinedPlace !== true && this.props.fetchDetails === true) {
      if (rowData.isLoading === true) {
        // already requesting
        return;
      }

      this._abortRequests();

      // display loader
      this._enableRowLoader(rowData);

      // fetch details
      const request = new XMLHttpRequest();
      this._requests.push(request);
      request.timeout = this.props.timeout;
      request.ontimeout = this.props.onTimeout;
      request.onreadystatechange = () => {
        if (request.readyState !== 4) {
          return;
        }
        if (request.status === 200) {
          const responseJSON = JSON.parse(request.responseText);
          if (responseJSON.status === 'OK') {
            const details = responseJSON.result;
            this._disableRowLoaders();
            this._onBlur();

            this.setState({
              text: rowData.description,
            });

            delete rowData.isLoading;
            this.props.onPress(rowData, details);
          } else {
            this._disableRowLoaders();
            console.warn('google places autocomplete: ' + responseJSON.status);
          }
        } else {
          this._disableRowLoaders();
          console.warn('google places autocomplete: request could not be completed or has been aborted');
        }
      };
      request.open('GET', 'https://maps.googleapis.com/maps/api/place/details/json?' + Qs.stringify({
        key: this.props.query.key,
        placeid: rowData.place_id,
        language: this.props.query.language,
      }));
      request.send();
    } else if (rowData.isCurrentLocation === true) {

      // display loader
      this._enableRowLoader(rowData);


      this.setState({
        text: rowData.description,
      });
      this.triggerBlur(); // hide keyboard but not the results

      delete rowData.isLoading;

      this.getCurrentLocation();

    } else {
      this.setState({
        text: rowData.description,
      });

      this._onBlur();

      delete rowData.isLoading;

      let predefinedPlace = this._getPredefinedPlace(rowData);

      // sending predefinedPlace as details for predefined places
      this.props.onPress(predefinedPlace, predefinedPlace);
    }
  }

  _getPredefinedPlace(rowData: Result) {
    if (rowData.isPredefinedPlace !== true) {
      return rowData;
    }
    for (let i = 0; i < this.props.predefinedPlaces.length; i++) {
      if (this.props.predefinedPlaces[i].description === rowData.description) {
        return this.props.predefinedPlaces[i];
      }
    }
    return rowData;
  }

  _filterResultsByTypes(responseJSON: Object, types: [string]) {
    if (types.length === 0) {
      return responseJSON.results;
    }

    var results: [Result] = [];
    for (let i = 0; i < responseJSON.results.length; i++) {
      let found = false;
      for (let j = 0; j < types.length; j++) {
        if (responseJSON.results[i].types.indexOf(types[j]) !== -1) {
          found = true;
          break;
        }
      }
      if (found === true) {
        results.push(responseJSON.results[i]);
      }
    }
    return results;
  }

  _requestNearby(latitude: number, longitude: number) {
    this._abortRequests();
    if (latitude !== undefined && longitude !== undefined && latitude !== null && longitude !== null) {
      const request = new XMLHttpRequest();
      this._requests.push(request);
      request.timeout = this.props.timeout;
      request.ontimeout = this.props.onTimeout;
      request.onreadystatechange = () => {
        if (request.readyState !== 4) {
          return;
        }
        if (request.status === 200) {
          const responseJSON = JSON.parse(request.responseText);

          this._disableRowLoaders();

          if (typeof responseJSON.results !== 'undefined') {
            var results = [];
            if (this.props.nearbyPlacesAPI === 'GoogleReverseGeocoding') {
              results = this._filterResultsByTypes(responseJSON, this.props.filterReverseGeocodingByTypes);
            } else {
              results = responseJSON.results;
            }

            this.setState({
              dataSource: this.state.dataSource.cloneWithRows(this.buildRowsFromResults(results)),
            });
          }
          if (typeof responseJSON.error_message !== 'undefined') {
            console.warn('google places autocomplete: ' + responseJSON.error_message);
          }
        } else {
          // console.warn("google places autocomplete: request could not be completed or has been aborted");
        }
      };

      let url = '';
      if (this.props.nearbyPlacesAPI === 'GoogleReverseGeocoding') {
        // your key must be allowed to use Google Maps Geocoding API
        url = 'https://maps.googleapis.com/maps/api/geocode/json?' + Qs.stringify({
          latlng: latitude + ',' + longitude,
          key: this.props.query.key,
          ...this.props.GoogleReverseGeocodingQuery,
        });
      } else {
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?' + Qs.stringify({
          location: latitude + ',' + longitude,
          key: this.props.query.key,
          ...this.props.GooglePlacesSearchQuery,
        });
      }

      request.open('GET', url);
      request.send();
    } else {
      this._results = [];
      this.setState({
        dataSource: this.state.dataSource.cloneWithRows(this.buildRowsFromResults([])),
      });
    }
  }

  _request(text: string) {
    this._abortRequests();
    if (text.length >= this.props.minLength) {
      const request = new XMLHttpRequest();
      this._requests.push(request);
      request.timeout = this.props.timeout;
      request.ontimeout = this.props.onTimeout;
      request.onreadystatechange = () => {
        if (request.readyState !== 4) {
          return;
        }
        if (request.status === 200) {
          const responseJSON = JSON.parse(request.responseText);
          if (typeof responseJSON.predictions !== 'undefined') {
            this._results = responseJSON.predictions;
            this.setState({
              dataSource: this.state.dataSource.cloneWithRows(this.buildRowsFromResults(responseJSON.predictions)),
            });
          }
          if (typeof responseJSON.error_message !== 'undefined') {
            console.warn('google places autocomplete: ' + responseJSON.error_message);
          }
        } else {
          // console.warn("google places autocomplete: request could not be completed or has been aborted");
        }
      };
      request.open('GET', 'https://maps.googleapis.com/maps/api/place/autocomplete/json?&input=' + encodeURI(text) + '&' + Qs.stringify(this.props.query));
      request.send();
    } else {
      this._results = [];
      this.setState({
        dataSource: this.state.dataSource.cloneWithRows(this.buildRowsFromResults([])),
      });
    }
  }

  _onChangeText(text: string) {
    this._request(text);
    this.setState({
      text: text,
      listViewDisplayed: true,
    });
  }

  _getRowLoader() {
    if (Platform.OS === 'android') {
      return (
        <ProgressBarAndroid
          style={[defaultStyles.androidLoader, this.props.styles.androidLoader]}
          styleAttr="Inverse"
        />
      );
    }
    return (
      <ActivityIndicatorIOS
        animating={true}
        size="small"
      />
    );
  }

  _renderLoader(rowData: Result) {
    if (rowData.isLoading === true) {
      return (
        <View
          style={[defaultStyles.loader, this.props.styles.loader]}
        >
          {this._getRowLoader()}
        </View>
      );
    }
    return null;
  }

  _renderRow(rowData: Result = {}) {
    rowData.description = rowData.description || rowData.formatted_address || rowData.name;

    return (
      <TouchableHighlight
        onPress={() =>
          this._onPress(rowData)
        }
        underlayColor="#c8c7cc"
      >
        <View>
          <View style={[defaultStyles.row, this.props.styles.row, rowData.isPredefinedPlace ? this.props.styles.specialItemRow : {}]}>
            <Text
              style={[{flex: 1}, defaultStyles.description, this.props.styles.description, rowData.isPredefinedPlace ? this.props.styles.predefinedPlacesDescription : {}]}
              numberOfLines={1}
            >
              {rowData.description}
            </Text>
            {this._renderLoader(rowData)}
          </View>
          <View style={[defaultStyles.separator, this.props.styles.separator]} />
        </View>
      </TouchableHighlight>
    );
  }

  _onBlur() {
    this.triggerBlur();
    this.setState({listViewDisplayed: false});
  }

  _onFocus() {
    this.setState({listViewDisplayed: true});
  }

  _getListView() {
    if ((this.state.text !== '' || this.props.predefinedPlaces.length || this.props.currentLocation === true) && this.state.listViewDisplayed === true) {
      return (
        <ListView
          keyboardShouldPersistTaps={true}
          keyboardDismissMode="on-drag"
          style={[defaultStyles.listView, this.props.styles.listView]}
          dataSource={this.state.dataSource}
          renderRow={this._renderRow}
          automaticallyAdjustContentInsets={false}

          {...this.props}
        />
      );
    }

    return null;
  }

  render() {
    let { onChangeText, onFocus, ...userProps } = this.props.textInputProps;
    return (
      <View
        style={[{flex: 1}, this.props.styles.container]}
      >
        <TextInput
          { ...userProps }
          ref="textInput"
          autoFocus={this.props.autoFocus}
          style={[defaultStyles.textInput, this.props.styles.textInput]}
          onChangeText={onChangeText ? text => {this._onChangeText(text); onChangeText(text);} : this._onChangeText}
          value={this.state.text}
          placeholder={this.props.placeholder}
          onFocus={onFocus ? () => {this._onFocus(); onFocus();} : this._onFocus}
          clearButtonMode="while-editing"
        />
        {this._getListView()}
      </View>
    );
  }
}
