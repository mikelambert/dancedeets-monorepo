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

class SubEventLine extends Component {
  render() {
    return (
      <View style={eventStyles.subEventLine}>
        <Image key="image" source={this.icon()} style={eventStyles.subIcon} />
        <View style={eventStyles.subEventRightSide}>{this.textRender()}</View>
      </View>
    );
  }
}

class EventCategories extends SubEventLine {
  icon() {
    return require('./images/event-icons/categories.png');
  }
  textRender() {
    if (this.props.categories.length > 0) {
      return <Text
        numberOfLines={1}
        style={eventStyles.rowText} 
        >({this.props.categories.slice(0,8).join(', ')})</Text>
    } else {
      return null;
    }
  }
}

class EventDateTime extends SubEventLine {
  icon() {
    return require('./images/event-icons/datetime.png');
  }
  textRender() {
    if (this.props.start) {
      return <Text style={eventStyles.rowDateTime}>{this.props.start}</Text>
    } else {
      return null;
    }
  }
}

class EventVenue extends SubEventLine {
  icon() {
    return require('./images/event-icons/location.png');
  }
  textRender() {
    var components = [];
    if (this.props.venue.name) {
      components.push(<Text key="line1" style={eventStyles.rowText}>{this.props.venue.name}</Text>);
    }
    if (this.props.venue.address) {
      components.push(<Text key="line2" style={eventStyles.rowText}>{this.props.venue.address.city + ', ' + this.props.venue.address.country}</Text>);
    }
    return <View>{components}</View>
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
        <Text
          numberOfLines={2}
          style={eventStyles.rowTitle}>{this.props.event.name}</Text>
        <View style={eventStyles.subRow}>
          <EventCategories categories={this.props.event.annotations.categories} />
          <EventDateTime start={this.props.event.start_time} end={this.props.event.date_time} />
          <EventVenue venue={this.props.event.venue} />
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

var Dummy2 = React.createClass({
  render: function() {
    return      (
  <View style={styles.container}>

        <View style={styles.descriptionContainer}>
          <View style={styles.padding}/>
          <Text style={styles.descriptionText} numberOfLines={1} >
            Here is a really long text that you can do nothing about, its gonna be long wether you like it or not, so be prepared for it to go off screen. Right? Right..!
          </Text>
        </View>
  </View>);
  }
});

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
  subEventLine: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  subEventRightSide: {
    flex: 1.0,
  },
  subIcon: {
    marginTop: 5,
    marginRight: 5,
    height: 12,
    width: 12,
  }
});

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#000',
    flex: 1,
    justifyContent: 'center',
  },
});

AppRegistry.registerComponent('DancedeetsReact', () => DancedeetsReact);
