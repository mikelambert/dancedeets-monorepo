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
  const result: Array<any> = Object.entries(category.signups || {}).sort().map((x) => x[1]);
  return result;
}

class _UserRegistrationStatus extends React.Component {
  state: {
    isLoading: boolean;
  }

  constructor(props) {
    super(props);
    this.state = {isLoading: false};
  }

  render() {
    const registerButton = (
      <Button
        caption="Register"
        onPress={async () => {
          this.setState({isLoading: true});
          await this.props.onRegister(this.props.category);
          this.setState({isLoading: false});
        }}
        isLoading={this.state.isLoading}
        />
    );
    if (this.props.user) {
      const userId = this.props.user.profile.id;
      const signups = getCategorySignups(this.props.category);
      const signedUpTeams = signups.filter((signup) => userId in (signup.dancers || {}));
      if (signedUpTeams.length) {
        const teamTexts = signedUpTeams.map((team) => {
          return <HorizontalView style={styles.registrationLineOuter} key={team}>
            <CompactTeam team={team} style={styles.registrationIndent}/>
            <Button
              caption="Unregister"
              onPress={async () => {
                this.setState({isLoading: true});
                await this.props.onUnregister(this.props.category, team);
                this.setState({isLoading: false});
              }}
              isLoading={this.state.isLoading}
              />
          </HorizontalView>;
        });
        return <View>
          <HorizontalView style={styles.registrationLine}>
            <Image
              source={require('./images/green-check.png')}
              style={styles.registrationStatusIcon}
              />
            <Text style={styles.registrationStatusText}>Registered:</Text>
          </HorizontalView>
          {teamTexts}
        </View>;
      } else {
        return <HorizontalView style={styles.registrationLineOuter}>
          <HorizontalView style={styles.registrationLine}>
            <Image
              source={require('./images/red-x.png')}
              style={styles.registrationStatusIcon}
              />
            <Text style={styles.registrationStatusText}>Not Registered</Text>
          </HorizontalView>
          {registerButton}
        </HorizontalView>;
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
      storageKey="battleEvent"
      >{view}</TrackFirebase>;
  }
}
const BattleView = connect(
  state => ({
    battleEvent: state.firebase.battleEvent,
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
    const dancers = Object.keys(signup.dancers || {}).map((x) => <Text key={x} style={{marginLeft: 20}}>{signup.dancers[x].name}</Text>);
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
  state: {
    values: any;
  }

  constructor(props) {
    super(props);
    this.state = {values: {
      ...this.teamDefaults(),
      team_name: '',
    }};
    if (this.props.user) {
      this.state.values.dancer_name_1 = this.props.user.profile.name;
    }
    (this: any).handleValueChange = this.handleValueChange.bind(this);
  }

  computeDefaultTeamName() {
    const dancers = [];
    let index = 1;
    while (this.state.values['dancer_name_' + index]) {
      dancers.push(this.state.values['dancer_name_' + index]);
      index += 1;
    }
    return dancers.join(' and ');
  }

  teamIndices() {
    const requirements = this.props.category.signupRequirements;
    const zero_to_n = Array.from(Array(requirements.maxTeamSize).keys());
    return zero_to_n;
  }

  teamDefaults() {
    const defaults = {};
    this.teamIndices().forEach((index) => {
      defaults['dancer_name_' + (index + 1)] = '';
    });
    return defaults;
  }

  teamWidgets() {
    return this.teamIndices().map((index) =>
      <GiftedForm.TextInputWidget
        key={index}
        name={'dancer_name_' + (index + 1)}
        title={'Dancer ' + (index + 1)}
        placeholder=""

        {...this.textInputProps()}
        />
    );
  }

  teamValidators() {
    const validators = {};
    this.teamIndices().forEach((index) => {
      validators['dancer_name_' + (index + 1)] = {
        title: 'Dancer ' + (index + 1),
        validate: [],
      };
    });
    return validators;
  }

  textInputProps() {
    return {
      placeholderTextColor: 'rgba(255, 255, 255, 0.5)',
      keyboardAppearance: 'dark',

      clearButtonMode: 'while-editing',
      underlined: true,
      autoCorrect: false,
      autoCapitalize: 'words',
    };
  }

  fakeNavigator() {
    return {
      pop: () => this.props.navigatePop(),
    };
  }

  handleValueChange(values) {
    this.setState({values});
  }

  render() {
    const requirements = this.props.category.signupRequirements;

    let teamMember1 = [];
    let teamMembers = requirements.minTeamSize ? this.teamWidgets() : null;
    if (this.props.user) {
      teamMember1 = [
        <GiftedForm.HiddenWidget name="dancer_id_1" value={this.props.user.profile.id} />
      ,
        <GiftedForm.TextInputWidget
          name="dancer_name_1" // mandatory
          title="Dancer 1 (You)"
          validationImage={false}

          {...this.textInputProps()}
        />
      ];
      teamMembers = teamMembers ? teamMembers.slice(1) : null;
    }

    let teamName = null;
    if (requirements.needsTeamName) {
      teamName = <GiftedForm.TextInputWidget
        name="team_name" // mandatory
        title="Team Name"
        placeholder={this.computeDefaultTeamName()}

        {...this.textInputProps()}
      />;
    }
    return <MyGiftedForm
      navigator={this.fakeNavigator()}
      scrollEnabled={false}
      formName="signupForm" // GiftedForm instances that use the same name will also share the same states

      openModal={(route) => this.props.navigatePush(route)}

      defaults={this.state.values}

      validators={{
        team_name: {
          title: 'Team Name',
          validate: [],
        },
        ...this.teamValidators(),
      }}

      onValueChange={this.handleValueChange}
    >

      {teamMember1}
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
            const newValues = {...values};
            if (!newValues.team_name) {
              newValues.team_name = this.computeDefaultTeamName();
            }
            const result = await eventRegister('justeDebout', this.props.category.id, {team: newValues});
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
    this.props.navigatable.onNavigate({key: 'Register', title: `${displayName} Registration`, categoryId: category.id});
  }

  async onUnregister(category, teamToDelete) {
    const [teamKey, ] = Object.entries(category.signups || {}).filter(([key, team]) => team === teamToDelete)[0];
    await eventUnregister('justeDebout', category.id, teamKey);
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

    let category = null;

    switch (route.key) {
    case 'EventSignups':
      return <BattleView
        onSelected={(selectedCategory) => {
          //trackWithEvent('View Event', event);
          const displayName = categoryDisplayName(selectedCategory);
          this.props.navigatable.onNavigate({key: 'Category', title: displayName, categoryId: selectedCategory.id});
        }}
        onRegister={this.onRegister}
        onUnregister={this.onUnregister}
      />;
    case 'Category':
      category = this.props.battleEvent.categories.find((x) => x.id === route.categoryId);
      return <Category
        category={category}
        onRegister={this.onRegister}
        onUnregister={this.onUnregister}
        />;
    case 'Register':
      category = this.props.battleEvent.categories.find((x) => x.id === route.categoryId);
      return <RegistrationPage
        category={category}
        />;
    }
  }
}
export const EventSignupsView = connect(
  state => ({
    battleEvent: state.firebase.battleEvent,
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
  textInput: {
    height: 30,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    marginTop: 5,
  },
});
