
import React, {
  Component,
  Image,
  ListView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

import { ProportionalImage } from './ui';
import { Event } from './models';

class SubEventLine extends Component {
  render() {
    return (
      <View style={eventStyles.detailLine}>
        <Image key="image" source={this.icon()} style={eventStyles.detailIcon} />
        {this.textRender()}
      </View>
    );
  }
}

class EventCategories extends SubEventLine {
  icon() {
    return require('../images/event-icons/categories.png');
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
    return require('../images/event-icons/datetime.png');
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
    return require('../images/event-icons/location.png');
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
    var imageProps = this.props.event.getImageProps();
    return (
      <View style={eventStyles.row}>
        <TouchableOpacity onPress={this.props.onEventSelected} activeOpacity={0.5}>
          <ProportionalImage
            source={{uri: imageProps.url}}
            originalWidth={imageProps.width}
            originalHeight={imageProps.height}
            style={eventStyles.thumbnail}
          />
          <Text
            numberOfLines={2}
            style={eventStyles.rowTitle}>{this.props.event.name}</Text>
          <View style={eventStyles.eventIndent}>
            <EventCategories categories={this.props.event.annotations.categories} />
            <EventDateTime start={this.props.event.start_time} end={this.props.event.date_time} />
            <EventVenue venue={this.props.event.venue} />
          </View>
        </TouchableOpacity>
      </View>
    );
  }
}


class EventListView extends Component {
  constructor(props) {
    super(props);
  }
  render() {
    var onEventSelected = this.props.onEventSelected;
    return (
        <ListView
          dataSource={this.props.dataSource}
          renderRow={function(e) {
    return <EventRow
      event={new Event(e)}
      onEventSelected={onEventSelected}
    />
  }}

          initialListSize={50}
          pageSize={30}
        />
    );
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
  detailLine: {
    marginLeft: 20,
    flexDirection: 'row',
  },
  detailIcon: {
    marginTop: 5,
    marginRight: 5,
    height: 12,
    width: 12,
  }
});

module.exports = {
    EventListView,
};
