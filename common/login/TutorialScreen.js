import ViewPager from 'react-native-viewpager';
import React, {
  Component,
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

var PAGES = [
  'Page 0',
  'Page 1',
  'Page 2',
  'Page 3',
];

export default class TutorialScreen extends React.Component {
  constructor(props) {
    super(props);
    var dataSource = new ViewPager.DataSource({
      pageHasChanged: (p1, p2) => p1 !== p2,
    });
    this.state = {
      dataSource: dataSource.cloneWithPages(PAGES),
    }
    this._renderPage = this._renderPage.bind(this);
  }

  render() {
    return (
      <ViewPager
        style={this.props.style}
        dataSource={this.state.dataSource}
        renderPage={this._renderPage}
        isLoop={false}
        autoPlay={false}/>
    );
  }

  _renderPage(data: Object, pageID: number | string,) {
    if (pageID == 0) {
      return <Image
        style={styles.container}
        source={require('./images/LaunchScreen.jpg')}>
        <Image
          style={styles.container}
          source={require('./images/LaunchScreenText.png')}>
        </Image>
      </Image>;
    } else if (pageID == 1) {
      return <Image
        style={styles.container}
        source={require('./images/Onboard1.jpg')}>
        <Image
        style={[styles.container, styles.centerItems]}
          source={require('./images/Onboard1Text.png')}>
          <Text style={styles.onboardHeader}>Take a Trip:</Text>
          <View style={styles.onboardList}>
            <Text style={styles.onboardListItem}>Meet local dancers</Text>
            <Text style={styles.onboardListItem}>Hit up dance events</Text>
          </View>
        </Image>
      </Image>;
    } else if (pageID == 2) {
      return <Image
        style={[styles.container, styles.centerItems]}
        source={require('./images/Onboard2.jpg')}>
        <Text style={styles.onboardHeader}>Learn to Dance:</Text>
        <View style={styles.onboardList}>
          <Text style={styles.onboardListItem}>Take a class</Text>
          <Text style={styles.onboardListItem}>Watch a show</Text>
          <Text style={styles.onboardListItem}>Hit the clubs</Text>
        </View>
      </Image>;
    } else if (pageID == 3) {
      return <View style={styles.container}>
      <Image
        style={styles.container}
        source={require('./images/Onboard3.jpg')}>
        <Image
          style={[styles.container, styles.centerItems, styles.topAndBottom]}
          source={require('./images/Onboard3Text.png')}>
          <View style={styles.centerItems}>
            <Text style={styles.onboardHeader}>Promote your Scene:</Text>
            <View style={styles.onboardList}>
              <Text style={styles.onboardListItem}>Share your event</Text>
              <Text style={styles.onboardListItem}>Share your cities' events</Text>
              <Text style={styles.onboardListItem}>Reach dancers worldwide</Text>
              <Text style={styles.onboardListItem}>and join our 90,000+ events</Text>
            </View>
          </View>
          <View style={[styles.centerItems, styles.bottomBox]}>
            <TouchableOpacity activeOpacity={0.7}><Text style={[styles.bottomLink, styles.purpleButton]}>Login with Facebook</Text></TouchableOpacity>
            <TouchableOpacity activeOpacity={0.7}><Text style={[styles.bottomLink, styles.bottomLowerLink, styles.bottomThinLink]}>Don't want to login?</Text></TouchableOpacity>
          </View>
        </Image>
      </Image>
      </View>
    }
  }
}

var styles = StyleSheet.create({
  topAndBottom: {
    justifyContent: 'space-between',
  },
  absolute: {
    position: 'absolute',
    flex: 1,
    alignItems: 'center',
  },
  onboardHeader: {
    color: 'white',
    top: 60,
    fontSize: 30,
    fontWeight: 'bold',
  },
  onboardList: {
    top: 80,
  },
  onboardListItem: {
    color: 'white',
    lineHeight: 35,
    fontSize: 20,
    fontWeight: 'bold',
  },
  bottomBox: {
    height: 125,
  },
  bottomLink: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 20,
    top: 0,
  },
  bottomLowerLink: {
    top: 20,
  },
  bottomThinLink: {
    fontWeight: 'normal',
  },
  purpleButton: {
    paddingVertical: 7,
    paddingHorizontal: 15,
    borderWidth: 1,
    borderColor: 'white',
    backgroundColor: '#4F5086',
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
