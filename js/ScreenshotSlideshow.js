import React from 'react';

import {
  TouchableHighlight,
  View,
} from 'react-native';

export default class ScreenshotSlideshow extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      page: 0,
    };
    this.transitionPage = this.transitionPage.bind(this);
  }

  transitionPage() {
    switch (this.state.page) {
      case 0:
        console.log('0');
        break;
      case 1:
        console.log('1');
        break;
    }
    this.setState({page: this.state.page + 1});
  }

  render() {
    return <View>
      {this.props.children}
      <TouchableHighlight
        style={{
          position: 'absolute',
          top: 0,
          bottom: 0,
          left: 0,
          right: 0,
        }}
        onPress={this.transitionPage}
        testID="mainButton">
        <View />
      </TouchableHighlight>
    </View>;
  }
}
