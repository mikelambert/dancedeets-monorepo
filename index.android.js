/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 */

import React, {
  AppRegistry,
  Component,
  ListView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { EventListView } from './common/events';

class DancedeetsReact extends Component {
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
        <EventListView dataSource={this.state.dataSource} />
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

  fetchData() {
    fetch("http://www.dancedeets.com/api/v1.2/search?location=Taipei&time_period=UPCOMING")
      .then((response) => response.json())
      .then((responseData) => {
        console.log(responseData);
        this.setState({
          dataSource: this.state.dataSource.cloneWithRows(responseData.results),
          loaded: true,
        });
      })
      .done();
  }
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#000',
    flex: 1,
    justifyContent: 'center',
  },
});

AppRegistry.registerComponent('DancedeetsReact', () => DancedeetsReact);
