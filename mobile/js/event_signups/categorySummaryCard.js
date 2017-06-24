/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Animated,
  Dimensions,
  Image,
  StyleSheet,
  View,
  ViewPropTypes,
} from 'react-native';
import { injectIntl, defineMessages } from 'react-intl';
import { connect } from 'react-redux';
import danceStyles from 'dancedeets-common/js/styles';
import danceStyleIcons from 'dancedeets-common/js/styles/icons';
import type { Dispatch, User } from '../actions/types';
import { categoryDisplayName, getCategorySignups } from './models';
import { purpleColors } from '../Colors';
import {
  Button,
  Card,
  HorizontalView,
  normalize,
  ProportionalImage,
  semiNormalize,
  Text,
} from '../ui';
import type { BattleCategory, Signup } from './models';

// Try to make our boxes as wide as we can...
let boxWidth = normalize(350);
// ...and only start scaling them non-proportionally on the larger screen sizes,
// so that we do 3-4 columns
if (Dimensions.get('window').width >= 1024) {
  boxWidth = semiNormalize(350);
}

class CompactTeam extends React.Component {
  props: {
    style: ViewPropTypes.style,
    team: Signup,
  };

  render() {
    return (
      <Text style={[this.props.style, styles.registrationStatusText]}>
        {this.props.team.teamName}
      </Text>
    );
  }
}
class _UserRegistrationStatus extends React.Component {
  props: {
    category: BattleCategory,
    onRegister: (category: BattleCategory) => void,
    onUnregister: (category: BattleCategory, team: Signup) => void,

    // Self-managed props
    user: ?User,
  };

  state: {
    isLoading: boolean,
  };

  constructor(props) {
    super(props);
    this.state = { isLoading: false };
  }

  render() {
    const registerButton = (
      <Button
        caption="Register"
        onPress={async () => {
          this.setState({ isLoading: true });
          await this.props.onRegister(this.props.category);
          this.setState({ isLoading: false });
        }}
        isLoading={this.state.isLoading}
      />
    );
    if (this.props.user) {
      const userId = this.props.user.profile.id;
      const signups = getCategorySignups(this.props.category);
      const signedUpTeams = signups.filter(signup => {
        const dancerIds = signup.dancers.map(x => x.id);
        return dancerIds.includes(userId);
      });
      if (signedUpTeams.length) {
        const teamTexts = signedUpTeams.map(team =>
          <HorizontalView style={styles.registrationLineOuter} key={team}>
            <CompactTeam team={team} style={styles.registrationIndent} />
            <Button
              caption="Unregister"
              onPress={async () => {
                this.setState({ isLoading: true });
                await this.props.onUnregister(this.props.category, team);
                this.setState({ isLoading: false });
              }}
              isLoading={this.state.isLoading}
            />
          </HorizontalView>
        );
        return (
          <View>
            <HorizontalView style={styles.registrationLine}>
              <Image
                source={require('./images/green-check.png')}
                style={styles.registrationStatusIcon}
              />
              <Text style={styles.registrationStatusText}>Registered:</Text>
            </HorizontalView>
            {teamTexts}
          </View>
        );
      } else {
        return (
          <HorizontalView style={styles.registrationLineOuter}>
            <HorizontalView style={styles.registrationLine}>
              <Image
                source={require('./images/red-x.png')}
                style={styles.registrationStatusIcon}
              />
              <Text style={styles.registrationStatusText}>Not Registered</Text>
            </HorizontalView>
            {registerButton}
          </HorizontalView>
        );
      }
    } else {
      return registerButton;
    }
  }
}
const UserRegistrationStatus = connect(
  state => ({
    user: state.user.userData,
  }),
  (dispatch: Dispatch, props) => ({})
)(injectIntl(_UserRegistrationStatus));

class CategorySummaryCard extends React.Component {
  props: {
    category: BattleCategory,
    onRegister: (category: BattleCategory) => void,
    onUnregister: (category: BattleCategory, team: Signup) => void,
  };

  _root: View;

  setNativeProps(props: any) {
    this._root.setNativeProps(props);
  }

  dancerIcons(category: BattleCategory) {
    const display = category.display;
    const teamSize = Math.max(category.rules.teamSize, 1);

    const images = [];
    const imageWidth = (boxWidth - 20) / (2 * Math.max(teamSize, 2));
    for (let i = 0; i < teamSize; i += 1) {
      images.push(
        <ProportionalImage
          key={i}
          resizeDirection="width"
          source={danceStyleIcons[display.styleIcon]}
          originalWidth={danceStyles[display.styleIcon].width}
          originalHeight={danceStyles[display.styleIcon].height}
          resizeMode="contain"
          style={{
            height: imageWidth,
          }}
        />
      );
    }
    return <HorizontalView>{images}</HorizontalView>;
  }

  render() {
    const displayName = categoryDisplayName(this.props.category);
    const dancerIcons = this.dancerIcons(this.props.category);
    return (
      <View
        style={{
          width: boxWidth,
          backgroundColor: purpleColors[2],
          padding: 5,
          borderRadius: 10,
        }}
        ref={x => {
          this._root = x;
        }}
      >
        <HorizontalView style={{ justifyContent: 'space-between' }}>
          <View>{dancerIcons}</View>
          <Animated.View
            style={{ position: 'relative', transform: [{ skewY: '-180deg' }] }}
          >
            {dancerIcons}
          </Animated.View>
        </HorizontalView>
        <Text
          style={{
            marginVertical: 10,
            textAlign: 'center',
            fontWeight: 'bold',
            fontSize: semiNormalize(30),
            lineHeight: semiNormalize(34),
          }}
        >
          {displayName}
        </Text>
        <UserRegistrationStatus
          category={this.props.category}
          onRegister={this.props.onRegister}
          onUnregister={this.props.onUnregister}
        />
      </View>
    );
  }
}
export default CategorySummaryCard;

const checkSize = 20;
const checkMargin = 10;
let styles = StyleSheet.create({
  registrationLine: {
    alignItems: 'center',
  },
  registrationLineOuter: {
    justifyContent: 'space-between',
    alignItems: 'center',
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
