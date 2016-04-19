import ViewPager from 'react-native-viewpager';
import React, {
  Component,
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import LoginButton from './LoginButton';

var PAGES = [
  'Page 0',
  'Page 1',
  'Page 2',
  'Page 3',
];

class TopView extends React.Component {
  render() {
    var listItems = [];
    for (i in this.props.items) {
      listItems.push(<Text style={styles.onboardListItem}>{this.props.items[i]}</Text>);
    }
    return (
      <View style={styles.centerItems} >
        <Text style={styles.onboardHeader}>{this.props.header.toUpperCase()}</Text>
        <View style={styles.onboardList}>
          {listItems}
        </View>
      </View>
    );
  }
}

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
          <TopView header="Take a Trip:" items={[
            "Meet local dancers",
            "Hit up dance events",
          ]}/>
        </Image>
      </Image>;
    } else if (pageID == 2) {
      return <Image
        style={[styles.container, styles.centerItems]}
        source={require('./images/Onboard2.jpg')}>
        <TopView header="Learn to Dance:" items={[
          "Take a class",
          "Watch a show",
          "Hit the clubs",
        ]}/>
      </Image>;
    } else if (pageID == 3) {
      return <View style={styles.container}>
      <Image
        style={styles.container}
        source={require('./images/Onboard3.jpg')}>
        <Image
          style={[styles.container, styles.centerItems, styles.topAndBottom]}
          source={require('./images/Onboard3Text.png')}>
          <TopView header="Promote your event:" items={[
            "Share your event",
            "Share your city's events",
            "Reach dancers worldwide\nand join our 90,000 events",
          ]} />
          <View style={[styles.centerItems, styles.bottomBox]}>
            <LoginButton icon={require('./icons/facebook.png')} type="primary" caption="Login with Facebook"></LoginButton>
            <TouchableOpacity activeOpacity={0.7}><Text style={[styles.bottomLink, styles.bottomLowerLink, styles.bottomThinLink]}>DON'T WANT TO LOGIN?</Text></TouchableOpacity>
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
    fontSize: 14,
    top: 0,
  },
  bottomLowerLink: {
    top: 20,
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
