/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 */

import React, {
  AppRegistry,
  Component,
  Image,
  ListView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

var ProportionalImage = React.createClass({
  getInitialState() {
    return {
      style: {}
    };
  },

  propTypes: {
    originalWidth: React.PropTypes.number.isRequired,
    originalHeight: React.PropTypes.number.isRequired,
  },

  onLayout(e) {
    var layout = e.nativeEvent.layout;
    var aspectRatio = this.props.originalWidth / this.props.originalHeight;
    var measuredHeight = layout.width / aspectRatio;
    var currentHeight = layout.height;

    if (measuredHeight != currentHeight) {
      this.setState({
        style: {
          height: measuredHeight
        }
      });
    }
  },

  render() {
    // We catch the onLayout in the view, find the size, then resize the child (before it is laid out?)
    return (
      <View
        onLayout={this.onLayout}
        >
        <Image
          {...this.props}
          style={[this.props.style, this.state.style]}
        />
      </View>
    );
  }
});

class Event {
  constructor(eventData) {
    for (var attr in eventData) {
      if (eventData.hasOwnProperty(attr)) {
        this[attr] = eventData[attr];
      }
    }
    return this;
  }

  getImageProps() {
    var url = this.picture;
    var width = 100;
    var height = 100;
    if (this.cover != null && this.cover.images.length > 0) {
      var image = this.cover.images[0];
      url = image.source;
      width = image.width;
      height = image.height;
    }
    return {url, width, height};
  }

}

class EventRow extends Component {

  render() {
    console.log(this.props.event);
    var imageProps = this.props.event.getImageProps();
    return (
      <View style={eventStyles.row}>
        <ProportionalImage
          source={{uri: imageProps.url}}
          originalWidth={imageProps.width}
          originalHeight={imageProps.height}
          style={eventStyles.thumbnail}
        />
        <Text style={eventStyles.rowTitle}>{this.props.event.name}</Text>
        <View style={eventStyles.subRow}>
          <Text style={eventStyles.rowText}>{this.props.event.annotations.categories+' '}</Text>
          <Text style={eventStyles.rowDateTime}>{this.props.event.start_time+' '}</Text>
          <Text style={eventStyles.rowText}>{this.props.event.venue.name+' '}</Text>
        </View>
      </View>
    );
  }
}


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
        <ListView
          dataSource={this.state.dataSource}
          renderRow={(e) => <EventRow event={new Event(e)} />}
          style={styles.listView}
          initialListSize={50}
          pageSize={30}

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

const eventStyles = StyleSheet.create({
  thumbnail: {
    flex: 1,
  },
  row: {
    flex: 1,
    marginLeft: 5,
    marginRight: 5,
    marginBottom: 20,
    justifyContent: 'flex-start',
    alignItems: 'stretch',
  },
  rowTitle: {
    fontSize: 24,
    color: '#70C0FF',
  },
  rowDateTime: {
    color: '#C0FFC0',
  },
  rowText: {
    color: 'white',
  },
  subRow: {
    marginLeft: 20,
  },
});

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#000',
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

AppRegistry.registerComponent('DancedeetsReact', () => DancedeetsReact);
