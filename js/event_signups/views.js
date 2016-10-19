/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  AlertIOS,
  Animated,
  Dimensions,
  Image,
  ListView,
  StyleSheet,
  TouchableHighlight,
  View,
} from 'react-native';
import _ from 'lodash/string';
import { track } from '../store/track';
import YouTube from 'react-native-youtube';
import { FeedListView } from '../learn/BlogList';
import {
  Button,
  HorizontalView,
  Text,
} from '../ui';
import { purpleColors } from '../Colors';
import shallowEqual from 'fbjs/lib/shallowEqual';
import styleEqual from 'style-equal';
import {
  injectIntl,
  defineMessages,
} from 'react-intl';
import languages from '../languages';
import {
  Card,
  semiNormalize,
  normalize,
  ProportionalImage,
} from '../ui';
import { connect } from 'react-redux';
import type { Dispatch } from '../actions/types';
import {
  setTutorialVideoIndex,
} from '../actions';
import { googleKey } from '../keys';
import {
  categoryDisplayName,
} from './models';
import type {
  Signup,
  CompetitionCategory,
} from './models';
import danceStyles from '../styles';
import FitImage from 'react-native-fit-image';

// Trying to emulate Just Debout
const battleEvent = require('./justeDebout.json');

// Try to make our boxes as wide as we can...
let boxWidth = normalize(350);
// ...and only start scaling them non-proportionally on the larger screen sizes,
// so that we do 3-4 columns
if (Dimensions.get('window').width >= 1024) {
  boxWidth = semiNormalize(350);
}
const boxMargin = 5;

class CompactTeam extends React.Component {
  render() {
    return <Text style={[this.props.style, styles.registrationStatusText]}>{this.props.team.teamName}</Text>;
  }
}
class _UserRegistrationStatus extends React.Component {
  render() {
    const userId = this.props.user.profile.id;
    const signedUpTeams = this.props.category.signups.filter((signup) => userId in signup.dancers);
    if (signedUpTeams.length) {
      const teamTexts = signedUpTeams.map((x) => {
        return <HorizontalView style={styles.registrationLine}>
          <CompactTeam key={x} team={x} style={styles.registrationIndent}/>
          <Button caption="Unregister" onPress={this.props.unregisterUser}/>
        </HorizontalView>;
      });
      return <View>
        <HorizontalView>
          <Image
            source={require('./images/green-check.png')}
            style={styles.registrationStatusIcon}
            />
          <Text style={styles.registrationStatusText}>Registered:</Text>
        </HorizontalView>
        {teamTexts}
      </View>;
    } else {
      return <HorizontalView style={styles.registrationLine}>
        <HorizontalView>
          <Image
            source={require('./images/red-x.png')}
            style={styles.registrationStatusIcon}
            />
          <Text style={styles.registrationStatusText}>Not Registered</Text>
        </HorizontalView>
        <Button caption="Register" onPress={this.props.registerUser}/>
      </HorizontalView>;
    }
  }
}
const UserRegistrationStatus = connect(
  state => ({
    user: state.user.userData,
  }),
  (dispatch: Dispatch, props) => ({
    registerUser: () => console.log('register:', props.category),
    unregisterUser: () => console.log('unregister:', props.category),
  }),
)(injectIntl(_UserRegistrationStatus));

class CategorySummaryView extends React.Component {
  _root: ReactElement<any>;

  dancerIcons(category: any) {
    const teamSize = Math.max(category.teamSize, 1);

    const images = [];
    const imageWidth = (boxWidth - 20) / (2 * Math.max(teamSize, 2));
    for (let i = 0; i < teamSize; i++) {
      images.push(<ProportionalImage
        key={i}
        resizeDirection="width"
        source={danceStyles[category.styleIcon].thumbnail}
        originalWidth={danceStyles[category.styleIcon].width}
        originalHeight={danceStyles[category.styleIcon].height}
        resizeMode="contain"
        style={{
          height: imageWidth,
        }}
      />);
    }
    return <HorizontalView>{images}</HorizontalView>;
  }

  render() {
    const displayName = categoryDisplayName(this.props.category);
    const dancerIcons = this.dancerIcons(this.props.category);
    return <View
      style={{
        width: boxWidth,
        backgroundColor: purpleColors[2],
        padding: 5,
        borderRadius: 10,
      }}
      ref={(x) => {
        this._root = x;
      }}
       >
      <HorizontalView style={{justifyContent: 'space-between'}}>
        <View>{dancerIcons}</View>
        <Animated.View style={{position:'relative',transform:[{skewY: '-180deg'}]}}>{dancerIcons}</Animated.View>
      </HorizontalView>
      <Text style={{marginVertical: 10, textAlign: 'center', fontWeight: 'bold', fontSize: semiNormalize(30), lineHeight: semiNormalize(34)}}>{displayName}</Text>
      <UserRegistrationStatus category={this.props.category}/>
    </View>;
  }

  setNativeProps(props) {
    this._root.setNativeProps(props);
  }
}

class _BattleView extends React.Component {
  constructor(props: any) {
    super(props);
    (this: any).renderHeader = this.renderHeader.bind(this);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderHeader() {
    return <FitImage
      source={{uri: this.props.battleEvent.headerLogoUrl}}
      style={{flex: 1, width: Dimensions.get('window').width}}
    />;
  }

  renderRow(category: any) {
    return <TouchableHighlight
      onPress={() => {
        this.props.onSelected(category);
      }}
      style={{
        margin: boxMargin,
        borderRadius: 10,
      }}
      >
      <CategorySummaryView category={category} />
    </TouchableHighlight>;
  }

  render() {
    return <FeedListView
      items={this.props.battleEvent.categories}
      renderHeader={this.renderHeader}
      renderRow={this.renderRow}
      contentContainerStyle={{
        alignSelf: 'center',
        justifyContent: 'flex-start',
        alignItems: 'center',
      }}
      />;
  }
}
const BattleView = injectIntl(_BattleView);

class _TeamList extends React.Component {
  constructor(props: any) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderRow(signup: Signup) {
    const dancers = Object.keys(signup.dancers).map((x) => <Text key={x} style={{marginLeft: 20}}>{signup.dancers[x].name}</Text>);
    return <Card>
      <Text>{signup.teamName}:</Text>
      {dancers}
    </Card>;
  }

  render() {
    return <FeedListView
      items={this.props.signups}
      renderRow={this.renderRow}
      />;
  }
}
const TeamList = injectIntl(_TeamList);

class _Category extends React.Component {
  constructor(props: any) {
    super(props);
  }

  render() {
    return <View style={{
      alignSelf: 'center',
      marginTop: 10,
      flex: 1,
    }}>
      <CategorySummaryView category={this.props.category}/>
      <Text>{this.props.category.signups.length} competitors:</Text>
      <TeamList signups={this.props.category.signups} />
    </View>;
  }
}
const Category = injectIntl(_Category);

class _EventSignupsView extends React.Component {
  render() {
    const { scene } = this.props.sceneProps;
    const { route } = scene;
    switch (route.key) {
    case 'EventSignups':
      return <BattleView
        onSelected={(category) => {
          //trackWithEvent('View Event', event);
          const displayName = categoryDisplayName(category);
          this.props.navigatable.onNavigate({key: 'Category', title: displayName, category: category});
        }}
        battleEvent={battleEvent}
      />;
    case 'Category':
      return <Category
        category={route.category}
        />;
    }
  }
}
export const EventSignupsView = injectIntl(_EventSignupsView);

const checkSize = 20;
const checkMargin = 10;
let styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  miniThumbnail: {
    height: 50,
    flex: 1,
  },
  registrationLine: {
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  registrationStatusIcon: {
    width: checkSize,
    height: checkSize,
    marginRight: checkMargin,
  },
  registrationIndent: {
    marginLeft: checkSize + checkMargin,
  },
  registrationStatusText: {
    fontSize: semiNormalize(20),
    lineHeight: semiNormalize(24),
  },
});
