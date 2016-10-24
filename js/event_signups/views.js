/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  Animated,
  Dimensions,
  Image,
  StyleSheet,
  TouchableHighlight,
  View,
} from 'react-native';
import _ from 'lodash/string';
import { track } from '../store/track';
import { FeedListView } from '../learn/BlogList';
import {
  Button,
  MyGiftedForm,
  MyGiftedSubmitWidget,
  HorizontalView,
  Text,
} from '../ui';
import {
  purpleColors,
  yellowColors,
} from '../Colors';
import {
  injectIntl,
  defineMessages,
} from 'react-intl';
import {
  navigatePop,
  navigatePush,
} from '../actions';
import {
  Card,
  normalize,
  ProportionalImage,
  semiNormalize,
} from '../ui';
import { connect } from 'react-redux';
import type { Dispatch } from '../actions/types';
import {
  categoryDisplayName,
} from './models';
import type {
  Signup,
} from './models';
import {
  eventRegister,
  eventUnregister,
} from '../api/dancedeets';
import danceStyles from '../styles';
import FitImage from 'react-native-fit-image';
import { TrackFirebase } from '../firestack';
import { GiftedForm } from 'react-native-gifted-form';

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

function getCategorySignups(category: Category): Array<Signup> {
  const result: Array<any> = Object.entries(category.signups).sort().map((x) => x[1]);
  return result;
}

class _UserRegistrationStatus extends React.Component {
  render() {
    const userId = this.props.user.profile.id;
    const signups = getCategorySignups(this.props.category);
    const signedUpTeams = signups.filter((signup) => userId in signup.dancers);
    if (signedUpTeams.length) {
      const teamTexts = signedUpTeams.map((team) => {
        return <HorizontalView style={styles.registrationLine} key={team}>
          <CompactTeam team={team} style={styles.registrationIndent}/>
          <Button caption="Unregister" onPress={() => this.props.onUnregister(this.props.category, team)}/>
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
        <Button caption="Register" onPress={() => this.props.onRegister(this.props.category)}/>
      </HorizontalView>;
    }
  }
}
const UserRegistrationStatus = connect(
  state => ({
    user: state.user.userData,
  }),
  (dispatch: Dispatch, props) => ({
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
      <UserRegistrationStatus
        category={this.props.category}
        onRegister={this.props.onRegister}
        onUnregister={this.props.onUnregister}
        />
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
      <CategorySummaryView
        category={category}
        onRegister={this.props.onRegister}
        onUnregister={this.props.onUnregister}
        />
    </TouchableHighlight>;
  }

  render() {
    let view = null;
    if (this.props.battleEvent) {
      view = <FeedListView
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
    return <TrackFirebase
      path="events/justeDebout"
      storageKey="eventSignup"
      >{view}</TrackFirebase>;
  }
}
const BattleView = connect(
  state => ({
    battleEvent: state.firebase.eventSignup,
  }),
  (dispatch: Dispatch, props) => ({
  }),
)(injectIntl(_BattleView));

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
      renderHeader={this.props.renderHeader}
      />;
  }
}
const TeamList = injectIntl(_TeamList);

class _Category extends React.Component {
  constructor(props: any) {
    super(props);
  }

  render() {
    const signups = getCategorySignups(this.props.category);
    return <TeamList signups={signups}
      renderHeader={() => <View
        style={{
          alignSelf: 'center',
          marginTop: 10,
        }}>
          <CategorySummaryView
            category={this.props.category}
            onRegister={this.props.onRegister}
            onUnregister={this.props.onUnregister}
          />
          <Text>{signups.length} competitors:</Text>
        </View>
      }
    />;
  }
}
const Category = injectIntl(_Category);


class _RegistrationPage extends React.Component {
  computeDefaultTeamName() {
    return 'Computed Team';
  }

  teamDefaults() {
    const requirements = this.props.category.signupRequirements;
    const validators = {};
    new Array(requirements.maxTeamSize).fill(null).forEach((x, index) => {
      validators['dancer_name_' + (index + 1)] = '';
    });
  }

  teamWidgets() {
    const requirements = this.props.category.signupRequirements;
    return new Array(requirements.maxTeamSize).fill(null).map((x, index) =>
      <GiftedForm.TextInputWidget
        key={index}
        name={'dancer_name_' + (index + 1)}
        title={'Dancer ' + (index + 1)}

        placeholderTextColor="rgba(255, 255, 255, 0.5)"
        keyboardAppearance="dark"

        placeholder=""
        clearButtonMode="while-editing"
        />
    );
  }

  teamValidators() {
    const requirements = this.props.category.signupRequirements;
    const validators = {};
    new Array(requirements.maxTeamSize).fill(null).forEach((x, index) => {
      validators['dancer_name_' + (index + 1)] = {
        title: 'Dancer ' + (index + 1),
        validate: [{
          validator: 'isLength',
          arguments: [3, 30],
          message: '{TITLE} must be between {ARGS[0]} and {ARGS[1]} characters'
        }]
      };
    });
  }

  fakeNavigator() {
    return {
      pop: () => this.props.navigatePop(),
    };
  }

  render() {
    const requirements = this.props.category.signupRequirements;

    const teamMembers = requirements.minTeamSize ? this.teamWidgets() : null;

    let teamName = null;
    if (requirements.needsTeamName) {
      teamName = <GiftedForm.TextInputWidget
        name="team_name" // mandatory
        title="Team Name"

        placeholderTextColor="rgba(255, 255, 255, 0.5)"
        keyboardAppearance="dark"

        placeholder={this.computeDefaultTeamName()}
        clearButtonMode="while-editing"
      />;
    }

    return <MyGiftedForm
      navigator={this.fakeNavigator()}
      scrollEnabled={false}
      formName="signupForm" // GiftedForm instances that use the same name will also share the same states

      openModal={(route) => this.props.navigatePush(route)}

      defaults={{
        team_name: this.computeDefaultTeamName(),
        ...this.teamDefaults(),
      }}

      validators={{
        team_name: {
          title: 'Team Name',
          validate: [{
            validator: 'isLength',
            arguments: [3, 30],
            message: '{TITLE} must be between {ARGS[0]} and {ARGS[1]} characters'
          }]
        },
        ...this.teamValidators(),
      }}

      // Can use this to implement Redux state storage
      onValueChange={null}
    >

      {teamMembers}

      <GiftedForm.SeparatorWidget />

      {teamName}

      <GiftedForm.SeparatorWidget />

      <MyGiftedSubmitWidget
        title="Register"
        onSubmit={async (isValid, values, validationResults, postSubmit = null, modalNavigator = null) => {
          if (isValid === true) {
            // prepare object

            /* Implement the request to your server using values variable
            ** then you can do:
            ** postSubmit(); // disable the loader
            ** postSubmit(['An error occurred, please try again']); // disable the loader and display an error message
            ** postSubmit(['Username already taken', 'Email already taken']); // disable the loader and display an error message
            ** GiftedFormManager.reset('signupForm'); // clear the states of the form manually. 'signupForm' is the formName used
            */
            const result = await eventRegister('justeDebout', this.props.category.id, {team: values});
            if (postSubmit) {
              postSubmit();
            }
            // Do we want this?
            //this.props.onRegisterSubmit();
            if (modalNavigator) {
              modalNavigator.pop();
            }
          }
        }}

      />
    </MyGiftedForm>;
  }
}
const RegistrationPage = connect(
  state => ({
    user: state.user.userData,
  }),
  (dispatch: Dispatch, props) => ({
    navigatePush: (route) => dispatch(navigatePush('EVENT_SIGNUPS_NAV', route)),
    navigatePop: (route) => dispatch(navigatePop('EVENT_SIGNUPS_NAV')),
  }),
)(injectIntl(_RegistrationPage));

class _EventSignupsView extends React.Component {
  constructor(props) {
    super(props);
    (this: any).onRegister = this.onRegister.bind(this);
    (this: any).onUnregister = this.onUnregister.bind(this);
  }

  onRegister(category) {
    const displayName = categoryDisplayName(category);
    this.props.navigatable.onNavigate({key: 'Register', title: `${displayName} Registration`, category: category});
  }

  onUnregister(category, team) {
    console.log('Unregister team ', team);
  }

  fakeNavigator() {
    return {
      pop: () => this.props.navigatePop(),
    };
  }

  render() {
    const { scene } = this.props.sceneProps;
    const { route } = scene;
    // Handle Gifted Form navigation
    if (route.renderScene) {
      return route.renderScene(this.fakeNavigator());
    }
    switch (route.key) {
    case 'EventSignups':
      return <BattleView
        onSelected={(category) => {
          //trackWithEvent('View Event', event);
          const displayName = categoryDisplayName(category);
          this.props.navigatable.onNavigate({key: 'Category', title: displayName, category: category});
        }}
        onRegister={this.onRegister}
        onUnregister={this.onUnregister}
      />;
    case 'Register':
      return <RegistrationPage
        category={route.category}
        />;
    case 'Category':
      return <Category
        category={route.category}
        onRegister={this.onRegister}
        onUnregister={this.onUnregister}
        />;
    }
  }
}
export const EventSignupsView = connect(
  state => ({
  }),
  (dispatch: Dispatch, props) => ({
    navigatePop: (route) => dispatch(navigatePop('EVENT_SIGNUPS_NAV')),
  }),
)(injectIntl(_EventSignupsView));

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
  textInput: {
    height: 30,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    marginTop: 5,
  },
});
