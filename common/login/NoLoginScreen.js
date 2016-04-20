import React, {
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import LoginButton from './LoginButton';

const NoLoginText1 = 
`DANCEDEETS NEEDS YOU!

Almost all our dance events are
discovered through dancers who log in.

When dancers login with Facebook,
we can discover and share their events
with the rest of the dance scene,
helping bring people closer together.

But without logged-in dancers,
we’d have nothing to share,
and dance promotion would be harder.

So you can help DanceDeets,
and help the dance culture,
by logging in below.`;

const NoLoginText2 = 
`Sorry to hear you don’t want to login!

You can always use our website,
without any login requirements:
http://www.dancedeets.com/

But unfortunately, we require that 
you log in to use the mobile app.

Hope you’ll forgive us!`;

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
      <NoLoginBase headerText={NoLoginText1}>
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
          <Text style={[styles.bottomLink, styles.bottomThinLink]}>STILL DON'T WANT TO LOGIN?</Text>
        </TouchableOpacity>
      </NoLoginBase>
    );
  }
}

export class StillNoLoginScreen extends React.Component {
  render() {
    return (
      <NoLoginBase headerText={NoLoginText2}>
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
          <Text style={[styles.bottomLink, styles.bottomThinLink]}>GO TO WEBSITE</Text>
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
