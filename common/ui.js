
import React, {
  Image,
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

module.exports = {
    ProportionalImage,
}
