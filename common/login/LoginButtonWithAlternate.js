import React, {
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import LoginButton from './LoginButton';


export default class LoginButtonWithAlternate extends React.Component {
  render() {
    return (
      <View style={[styles.centerItems, styles.bottomBox]}>
        <LoginButton
          icon={require('./icons/facebook.png')}
          type="primary"
          caption="Login with Facebook"
          onPress={this.props.onLogin}
        />
        <TouchableOpacity
          style={styles.bottomLinkBox}
          activeOpacity={0.7}
          onPress={this.props.onNoLogin}
        >
          <Text style={[styles.bottomLink]}>{this.props.noLoginText}</Text>
        </TouchableOpacity>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  bottomBox: {
    alignItems: 'center',
    height: 125,
  },
  bottomLink: {
    color: 'white',
    fontWeight: 'normal',
    fontSize: 14,
  },
  bottomLinkBox: {
    top: 10,
  },
});
