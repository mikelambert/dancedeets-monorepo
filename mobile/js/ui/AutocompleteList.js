/**
 * Copyright 2016 DanceDeets.
 * Modified from react-native-google-places-autocomplete.
 * @flow
 */

import React from 'react';
import {
  ActivityIndicator,
  FlatList,
  Platform,
  ProgressBarAndroid,
  TouchableHighlight,
  View,
} from 'react-native';
import Qs from 'qs';
import emojiFlags from 'emoji-flags';
import { HorizontalView } from './Misc';
import { Text } from './DDText';
import { googleKey } from '../keys';
import { semiNormalize } from '../ui/normalize';
import lookupCountryCode from '../util/lookupCountryCode';
import { getAddress } from '../util/geo';

type Term = {
  value: string,
};
type Result = {
  description: string,
  isCurrentLocation?: boolean,
  isLoading?: boolean,
  flag?: string,
  terms?: Term[],
};

type Props = {
  style?: View.PropTypes.style, // style for FlatList
  styles?: { [name: string]: View.PropTypes.style }, // styles for subcomponents
  onLocationSelected: (location: string) => void | Promise<void>,
  minLength: number,
  fetchDetails: boolean,
  textValue: () => string,
  query: Object,
  GoogleReverseGeocodingQuery: Object,
  predefinedPlaces: Array<Result>,
  currentLocation: boolean,
  currentLocationLabel: string,
  filterReverseGeocodingByTypes: string[],
  predefinedPlacesAlwaysVisible: boolean,
  queryLanguage: string,
};

function sleep(seconds) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve();
    }, seconds * 1000);
  });
}

export default class AutocompleteList extends React.Component {
  static defaultProps: Props = {
    onLocationSelected: x => {},
    minLength: 0,
    fetchDetails: false,
    textValue: () => '',
    queryLanguage: 'en', // language of the results
    query: {
      key: googleKey,
      types: '(regions)', // default: 'geocode'
      // types: 'geocode',
    },
    GoogleReverseGeocodingQuery: {},
    styles: {},
    predefinedPlaces: [],
    currentLocation: true,
    currentLocationLabel: 'Current location',
    filterReverseGeocodingByTypes: [
      'political',
      'locality',
      'administrative_area_level_3',
    ],
    predefinedPlacesAlwaysVisible: false,
  };

  props: Props;

  state: {
    listViewDisplayed: boolean,
    isLoadingLocation: boolean,
    results: Array<Result>,
  };

  _requests: XMLHttpRequest[] = [];

  constructor(props: any) {
    super(props);

    this.state = {
      listViewDisplayed: false,
      isLoadingLocation: false,
      results: [],
    };
    (this: any).onTextInputFocus = this.onTextInputFocus.bind(this);
    (this: any).onPress = this.onPress.bind(this);
    (this: any).onTextInputChangeText = this.onTextInputChangeText.bind(this);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  componentWillUnmount() {
    this.abortRequests();
  }

  onTextInputChangeText(text: string) {
    this.request(text);
    this.setState({
      listViewDisplayed: true,
    });
  }

  onTextInputBlur() {
    this.setState({ listViewDisplayed: false });
  }

  onTextInputFocus() {
    this.setState({ listViewDisplayed: true });
  }

  onPress(rowData: Result) {
    if (rowData.isCurrentLocation) {
      // display loader
      this.enableRowLoader();
      this.getCurrentLocation();
    } else {
      this.props.onLocationSelected(rowData.description);
    }
  }

  async getCurrentLocation() {
    this.abortRequests();
    try {
      const address = await getAddress();
      this.props.onLocationSelected(address);
    } catch (e) {
      console.warn(e);
      await sleep(0.5);
      this.disableRowLoaders();
    }
  }

  getRowLoader() {
    return <ActivityIndicator animating size="small" />;
  }

  buildRowsFromResults(): Array<Result> {
    const results = this.state.results;

    let res: ?(Result[]) = null;

    if (!results.length || this.props.predefinedPlacesAlwaysVisible) {
      res = this.props.predefinedPlaces.map(x => {
        let terms = null;
        if (x.description.includes(',')) {
          terms = x.description.split(new RegExp(', +'));
        } else {
          terms = x.description.split(new RegExp(' +'));
        }
        return {
          key: x.description,
          description: x.description,
          terms: terms.map(value => ({ value })),
        };
      });
      if (this.props.currentLocation) {
        res.unshift({
          key: 'Current Location',
          description: this.props.currentLocationLabel,
          isCurrentLocation: true,
          isLoading: this.state.isLoadingLocation,
        });
      }
    } else {
      res = [];
    }

    const fullResults = [...res, ...results].map(x => {
      if (!x.terms) {
        return x;
      }
      // Usually Google maps returns the country last, but sometimes it is returned first.
      // So let's handle both cases.
      const firstTerm = x.terms[0].value;
      const lastTerm = x.terms[x.terms.length - 1].value;
      const code = lookupCountryCode(lastTerm) || lookupCountryCode(firstTerm);
      const flag = emojiFlags.data.find(c => c.code === code);
      const emoji = flag != null ? flag.emoji : '';
      return { ...x, flag: emoji };
    });
    return fullResults;
  }

  abortRequests() {
    for (let i = 0; i < this._requests.length; i += 1) {
      this._requests[i].abort();
    }
    this._requests = [];
  }

  enableRowLoader() {
    this.setState({ isLoadingLocation: true });
  }

  disableRowLoaders() {
    this.setState({ isLoadingLocation: false });
  }

  createRequest(url: string) {
    const f = (resolve, reject) => {
      const request = new XMLHttpRequest();
      this._requests.push(request);
      request.onreadystatechange = () => {
        if (request.readyState !== 4) {
          return;
        }
        if (request.status === 200) {
          const responseJSON = JSON.parse(request.responseText);
          resolve(responseJSON);
        } else if (!request._aborted) {
          // Ignore errors due to intentionally-aborted requests
          reject({ request });
        }
      };

      request.open('GET', url);
      request.send();
    };
    return new Promise(f.bind(this));
  }

  async request(text: string) {
    this.abortRequests();
    if (text.length >= this.props.minLength) {
      const query = Object.assign({}, this.props.query, {
        language: this.props.queryLanguage,
      });
      const url = `https://maps.googleapis.com/maps/api/place/autocomplete/json?&input=${encodeURI(
        text
      )}&${Qs.stringify(query)}`;
      try {
        const responseJSON = await this.createRequest(url);
        if (typeof responseJSON.predictions !== 'undefined') {
          this.setState({ results: responseJSON.predictions });
        }
        if (typeof responseJSON.error_message !== 'undefined') {
          console.warn(
            `google places autocomplete: ${responseJSON.error_message}`
          );
        }
      } catch (error) {
        console.warn('AutoComplete Http Error', error);
      }
    } else {
      this.setState({ results: [] });
    }
  }

  renderLoader(rowData: Result) {
    if (rowData.isLoading) {
      return (
        <HorizontalView
          style={[defaultStyles.loader, this.props.styles.loader]}
        >
          {this.getRowLoader()}
        </HorizontalView>
      );
    }
    return null;
  }

  renderRow(row) {
    const rowData = row.item;
    let emojiFlag = null;
    // Emojiflags don't work so well on Android?
    if (
      Platform.OS === 'ios' ||
      (Platform.OS === 'android' && Platform.Version >= 21)
    ) {
      emojiFlag = (
        <Text
          style={[
            defaultStyles.flag,
            defaultStyles.description,
            this.props.styles.description,
          ]}
        >
          {rowData.flag}
        </Text>
      );
    }

    return (
      <TouchableHighlight
        onPress={() => this.onPress(rowData)}
        underlayColor="#c8c7cc"
      >
        <View>
          <HorizontalView style={[defaultStyles.row, this.props.styles.row]}>
            {emojiFlag}

            <Text
              style={[
                { flex: 1 },
                defaultStyles.description,
                this.props.styles.description,
              ]}
              numberOfLines={1}
            >
              {rowData.description}
            </Text>
            {this.renderLoader(rowData)}
          </HorizontalView>
        </View>
      </TouchableHighlight>
    );
  }

  render() {
    const data = this.buildRowsFromResults();
    const { style, ...otherProps } = this.props;
    if (
      (this.props.textValue() !== '' ||
        this.props.predefinedPlaces.length ||
        this.props.currentLocation === true) &&
      this.state.listViewDisplayed === true
    ) {
      return (
        <FlatList
          data={data}
          scrollEnabled={false}
          keyboardShouldPersistTaps="always"
          keyboardDismissMode="on-drag"
          style={[defaultStyles.listView, this.props.styles.listView, style]}
          renderItem={this.renderRow}
          automaticallyAdjustContentInsets={false}
          {...otherProps}
        />
      );
    }

    return null;
  }
}

const defaultStyles = {
  textInput: {},
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
  },
};
