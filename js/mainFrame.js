/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React, {
  ListView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { EventListView } from './events';

import type { Event } from './models';

export default class EventListContainer extends React.Component {
  props: {
    onEventSelected: (x: Event) => void,
  };

  state: {
    dataSource: ListView.DataSource,
    loaded: boolean,
  };

  constructor(props) {
    super(props);
    this.state = {
      dataSource: new ListView.DataSource({
        rowHasChanged: (row1, row2) => row1 !== row2,
      }),
      loaded: false,
    };
  }

  componentDidMount() {
    this.fetchData();
  }

  render() {
    if (!this.state.loaded) {
      return this.renderLoadingView();
    }

    return (
      <View
        style={styles.container}>
        <EventListView
          dataSource={this.state.dataSource}
          onEventSelected={this.props.onEventSelected}
        />
      </View>
    );
  }

  renderLoadingView() {
    return (
      <View style={styles.container}>
        <Text>
          Loading events...
        </Text>
      </View>
    );
  }

  async fetchData() {
    const response = await fetch('http://www.dancedeets.com/api/v1.2/search?location=South Africa&time_period=UPCOMING');
    // TODO: This is the slow part. :( Can we request less data?
    var responseData = await response.json();
    this.setState({
      dataSource: this.state.dataSource.cloneWithRows(responseData.results),
      loaded: true,
    });
  }
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#000',
    flex: 1,
    justifyContent: 'center',
  },
});
