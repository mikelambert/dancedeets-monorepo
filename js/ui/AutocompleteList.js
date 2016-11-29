/**
 * Copyright 2016 DanceDeets.
 * Modified from react-native-google-places-autocomplete.
 * @flow
 */

import React from 'react';
import {
  ActivityIndicator,
  ListView,
  Platform,
  ProgressBarAndroid,
  TouchableHighlight,
  View,
} from 'react-native';
import {HorizontalView} from './Misc';
import {Text} from './DDText';
import Qs from 'qs';
import emojiFlags from 'emoji-flags';
import { googleKey } from '../keys';
import {
  semiNormalize,
} from '../ui/normalize';
import lookupCountryCode from '../util/lookupCountryCode';
import { getAddress } from '../util/geo';

type Term = {
  value: string;
};
type Result = {
  description: string;
  isCurrentLocation?: boolean;
  isLoading?: boolean;
  flag?: string;
  terms?: Term[];
};


type Props = {
  style: Object, // style for ListView
  styles: Object, // styles for subcomponents
  onLocationSelected: (location: string) => (void | Promise<void>),
  minLength: number,
  fetchDetails: boolean,
  textValue: () => string,
  query: Object,
  GoogleReverseGeocodingQuery: Object,
  predefinedPlaces: Result[],
  currentLocation: boolean,
  currentLocationLabel: string,
  filterReverseGeocodingByTypes: string[],
  predefinedPlacesAlwaysVisible: boolean,
  queryLanguage: string,
};

export default class AutocompleteList extends React.Component {
  state: {
    dataSource: ListView.DataSource,
    listViewDisplayed: boolean,
  };

  _results: Result[] = [];
  _requests: XMLHttpRequest[] = [];


  static defaultProps: Props = {
    onLocationSelected: (x) => {},
    minLength: 0,
    fetchDetails: false,
    textValue: () => '',
    queryLanguage: 'en', // language of the results
    query: {
      key: googleKey,
      types: '(regions)', // default: 'geocode'
      //types: 'geocode',
    },
    GoogleReverseGeocodingQuery: {
    },
    style: {},
    styles: {},
    predefinedPlaces: [],
    currentLocation: true,
    currentLocationLabel: 'Current location',
    filterReverseGeocodingByTypes: ['political', 'locality', 'administrative_area_level_3'],
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
      dataSource: ds.cloneWithRows(this.buildRowsFromResults([])),
      listViewDisplayed: false,
    };
    (this: any).onTextInputFocus = this.onTextInputFocus.bind(this);
    (this: any)._onPress = this._onPress.bind(this);
    (this: any).onTextInputChangeText = this.onTextInputChangeText.bind(this);
    (this: any)._renderRow = this._renderRow.bind(this);
  }

  buildRowsFromResults(results: Result[]): Result[] {
    var res: ?Result[] = null;

    if (results.length === 0 || this.props.predefinedPlacesAlwaysVisible === true) {
      res = this.props.predefinedPlaces.map((x) => {
        let terms = null;
        if (x.description.includes(',')) {
          terms = x.description.split(new RegExp(', +'));
        } else {
          terms = x.description.split(new RegExp(' +'));
        }
        return {
          description: x.description,
          terms: terms.map((value) => {return {value: value};}),
        };
      });
      if (this.props.currentLocation === true) {
        res.unshift({
          description: this.props.currentLocationLabel,
          isCurrentLocation: true,
        });
      }
    } else {
      res = [];
    }

    var fullResults = [...res, ...results];
    fullResults.forEach((x) => {
      if (!x.terms) {
        return;
      }
      // Usually Google maps returns the country last, but sometimes it is returned first.
      // So let's handle both cases.
      const firstTerm = x.terms[0].value;
      const lastTerm = x.terms[x.terms.length - 1].value;
      const code = lookupCountryCode(lastTerm) || lookupCountryCode(firstTerm);
      const flag = emojiFlags.data.find((c) => c.code == code);
      x.flag = flag != null ? flag.emoji : '';
    });
    return fullResults;
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

  async getCurrentLocation() {
    this._abortRequests();
    try {
      const address = await getAddress();
      this.props.onLocationSelected(address);
    } catch (e) {
      this._disableRowLoaders();
      console.warn(e);
    }
  }

  _enableRowLoader(rowData: Result) {

    let rows = this.buildRowsFromResults(this._results);
    for (let i = 0; i < rows.length; i++) {
      if (rows[i].isCurrentLocation === true && rowData.isCurrentLocation === true) {
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
    if (rowData.isCurrentLocation === true) {
      // display loader
      this._enableRowLoader(rowData);
      delete rowData.isLoading;
      this.getCurrentLocation();
    } else {
      delete rowData.isLoading;
      this.props.onLocationSelected(rowData.description);
    }
  }

  _filterResultsByTypes(responseJSON: Object, types: string[]) {
    if (types.length === 0) {
      return responseJSON.results;
    }

    var results: Object[] = [];
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

  createRequest(url: string) {
    const f = function (resolve, reject) {
      const request = new XMLHttpRequest();
      this._requests.push(request);
      request.onreadystatechange = () => {
        if (request.readyState !== 4) {
          return;
        }
        if (request.status === 200) {
          const responseJSON = JSON.parse(request.responseText);
          resolve(responseJSON);
        } else {
          reject(request.status);
        }
      };

      request.open('GET', url);
      request.send();
    };
    return new Promise(f.bind(this));
  }

  _request(text: string) {
    this._abortRequests();
    if (text.length >= this.props.minLength) {
      const query = Object.assign({}, this.props.query, {language: this.props.queryLanguage});
      const url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?&input=' + encodeURI(text) + '&' + Qs.stringify(query);
      this.createRequest(url).then((responseJSON) => {
        if (typeof responseJSON.predictions !== 'undefined') {
          this._results = responseJSON.predictions;
          this.setState({
            dataSource: this.state.dataSource.cloneWithRows(this.buildRowsFromResults(responseJSON.predictions)),
          });
        }
        if (typeof responseJSON.error_message !== 'undefined') {
          console.warn('google places autocomplete: ' + responseJSON.error_message);
        }
      });
    } else {
      this._results = [];
      this.setState({
        dataSource: this.state.dataSource.cloneWithRows(this.buildRowsFromResults([])),
      });
    }
  }

  onTextInputChangeText(text: string) {
    this._request(text);
    this.setState({
      listViewDisplayed: true,
    });
  }

  _getRowLoader() {
    return (
      <ActivityIndicator
        animating={true}
        size="small"
      />
    );
  }

  _renderLoader(rowData: Result) {
    if (rowData.isLoading === true) {
      return (
        <HorizontalView
          style={[defaultStyles.loader, this.props.styles.loader]}
        >
          {this._getRowLoader()}
        </HorizontalView>
      );
    }
    return null;
  }

  _renderRow(rowData: Result) {
    let emojiFlag = null;
        // Emojiflags don't work so well on Android?
    if (Platform.OS === 'ios') {
      emojiFlag = <Text
        style={[defaultStyles.flag, defaultStyles.description, this.props.styles.description]}>
        {rowData.flag}
      </Text>;
    }

    return (
      <TouchableHighlight
        onPress={() =>
          this._onPress(rowData)
        }
        underlayColor="#c8c7cc"
      >
        <View>
          <HorizontalView style={[defaultStyles.row, this.props.styles.row]}>
            {emojiFlag}

            <Text
              style={[{flex: 1}, defaultStyles.description, this.props.styles.description]}
              numberOfLines={1}
            >
              {rowData.description}
            </Text>
            {this._renderLoader(rowData)}
          </HorizontalView>
        </View>
      </TouchableHighlight>
    );
  }

  onTextInputBlur() {
    this.setState({listViewDisplayed: false});
  }

  onTextInputFocus() {
    this.setState({listViewDisplayed: true});
  }

  render() {
    var {style, ...otherProps} = this.props;
    if ((this.props.textValue() !== '' || this.props.predefinedPlaces.length || this.props.currentLocation === true) && this.state.listViewDisplayed === true) {
      return (
        <ListView
          scrollEnabled={false}
          keyboardShouldPersistTaps={true}
          keyboardDismissMode="on-drag"
          style={[defaultStyles.listView, this.props.styles.listView, style]}
          dataSource={this.state.dataSource}
          renderRow={this._renderRow}
          automaticallyAdjustContentInsets={false}

          {...otherProps}
        />
      );
    }

    return null;
  }
}

const defaultStyles = {
  textInput: {
  },
  listView: {
    position: 'absolute',
    backgroundColor: '#222',
    // flex: 1,
    left: 0,
    right: 0,
  },
  row: {
    alignItems: 'center',
    paddingLeft: 15,
    height: semiNormalize(30),
  },
  separator: {
    height: 1,
    backgroundColor: '#c8c7cc',
  },
  description: {
    color: 'white',
    fontSize: semiNormalize(16),
  },
  loader: {
    // flex: 1,
    justifyContent: 'flex-end',
    height: 20,
  },
  androidLoader: {
    marginRight: -15,
  },
  flag: {
    width: 30,
  }
};
