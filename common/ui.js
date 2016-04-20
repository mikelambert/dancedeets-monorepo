
import React, {
  Image,
  View,
  Component,
} from 'react-native';

export class ProportionalImage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      style: {}
    };
    this.onLayout = this.onLayout.bind(this);
  }

  onLayout(e) {
    var layout = e.nativeEvent.layout;
    var aspectRatio = this.props.originalWidth / this.props.originalHeight;
    var measuredHeight = layout.width / aspectRatio;
    var currentHeight = layout.height;

    if (measuredHeight !== currentHeight) {
      this.setState({
        style: {
          height: measuredHeight
        }
      });
    }
  }

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
}

ProportionalImage.propTypes = {
  originalWidth: React.PropTypes.number.isRequired,
  originalHeight: React.PropTypes.number.isRequired,
};
