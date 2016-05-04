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

import { EventRow } from './uicomponents';
import { connect } from 'react-redux';

import { Event } from './models';
import { search } from '../api';

type Props = {
  onEventSelected: (x: Event) => void,
};


class EventListContainer extends React.Component {
  props: Props;

  state: {
    dataSource: ListView.DataSource,
    loaded: boolean,
  };

  constructor(props: Props) {
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
    return (
      <View style={styles.container}>
        {this.state.loaded ? this.renderListView() : this.renderLoadingView()}
      </View>
    );
  }

  renderListView() {
    var onEventSelected = this.props.onEventSelected;
    return (
      <ListView
        dataSource={this.state.dataSource}
        renderRow={(e) =>
          <EventRow
            event={new Event(e)}
            onEventSelected={onEventSelected}
          />
        }
        initialListSize={50}
        pageSize={30}
      />
    );
  }

  renderLoadingView() {
    return (
      <Text style={styles.loading}>
        Loading events...
      </Text>
    );
  }

  async fetchData() {
    try {
      const responseData = await search('South Africa', '', 'UPCOMING');
      // TODO: This is the slow part. :( Can we request less data?
      this.setState({
        dataSource: this.state.dataSource.cloneWithRows(responseData.results),
        loaded: true,
      });
    } catch (e) {
      // TODO: error fetching events.
      console.log('error fetching events', e);
    }
  }
}

export default connect()(EventListContainer);


const styles = StyleSheet.create({
  container: {
    backgroundColor: '#000',
    flex: 1,
    justifyContent: 'center',
  },
  loading: {
    color: 'white',
    textAlign: 'center',
  }
});
