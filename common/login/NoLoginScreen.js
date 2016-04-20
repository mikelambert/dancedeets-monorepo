import React, {
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import LoginButton from './LoginButton';

const NoLoginText =
`Almost all our dance events are
found when dancers like you log in.

Logging in shares your dance events
with DanceDeets, so our algorithm
can sort through everyone's events,
and share them with dancers everywhere.

But without any logged-in dancers,
we’d have nothing to share,
and promoting your events gets harder.

So please consider logging in,
to help us help your dance scene.

But if not, you're always able to use
our website without any login:

http://www.dancedeets.com/
`;

class NoLoginBase extends React.Component {
  render() {
    return (
      <View style={styles.container}>
        <Image
          style={[styles.container, styles.centerItems, styles.topAndBottom]}
          source={require('./images/Onboard4.jpg')}>
          <Text style={styles.topText}>{this.props.headerText}</Text>
          <View style={[styles.centerItems, styles.bottomBox]}>
            {this.props.children}
          </View>
        </Image>
      </View>
    );
  }
}

export class NoLoginScreen extends React.Component {
  render() {
    return (
      <NoLoginBase headerText={NoLoginText}>
        <LoginButton
          icon={require('./icons/facebook.png')}
          type="primary"
          caption="Login with Facebook"
          onPress={this.props.onLogin}
        />
        <TouchableOpacity
          style={styles.bottomLowerLink}
          activeOpacity={0.7}
          onPress={this.props.onNoLogin}
        >
          <Text style={[styles.bottomLink, styles.bottomThinLink]}>USE WEBSITE WITHOUT LOGIN</Text>
        </TouchableOpacity>
      </NoLoginBase>
    );
  }
}

const styles = StyleSheet.create({
  topAndBottom: {
    justifyContent: 'space-between',
  },
  topText: {
    top: 40,
    color: 'white',
    fontSize: 15,
  },
  bottomBox: {
    height: 125,
  },
  bottomLink: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
    top: 0,
  },
  bottomLowerLink: {
    top: 10,
  },
  bottomThinLink: {
    fontWeight: 'normal',
  },
  centerItems: {
    alignItems: 'center',
  },
  container: {
    flex: 1,
    backgroundColor: 'transparent',
    // Image's source contains explicit size, but we want
    // it to prefer flex: 1
    width: undefined,
    height: undefined,
  },
});
