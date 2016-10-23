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
  Card,
  defaultFont,
  normalize,
  ProportionalImage,
  TextInput,
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
import danceStyles from '../styles';
import FitImage from 'react-native-fit-image';
import firestack from '../firestack';
import { GiftedForm, GiftedFormManager } from 'react-native-gifted-form';

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
  state: {
    battleEvent: any;
  };

  constructor(props: any) {
    super(props);
    this.state = {battleEvent: null};
    (this: any).renderHeader = this.renderHeader.bind(this);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).handleValueChange = this.handleValueChange.bind(this);
  }

  handleValueChange(snapshot) {
    if (snapshot.val()) {
      this.setState({battleEvent: snapshot.val()});
    }
  }

  componentWillMount() {
    const eventPath = 'events/' + 'justeDebout';//this.props.eventId;
    firestack.database.ref(eventPath).on('value', this.handleValueChange);
  }

  componentWillUnmount() {
    const eventPath = 'events/' + 'justeDebout';//this.props.eventId;
    firestack.database.ref(eventPath).off('value', this.handleValueChange);
  }

  renderHeader() {
    return <FitImage
      source={{uri: this.state.battleEvent.headerLogoUrl}}
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
    if (!this.state.battleEvent) {
      return null;
    }
    return <FeedListView
      items={this.state.battleEvent.categories}
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
    return <TeamList signups={this.props.category.signups}
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
          <Text>{this.props.category.signups.length} competitors:</Text>
        </View>
      }
    />;
  }
}
const Category = injectIntl(_Category);

class RegistrationPage extends React.Component {
  render() {
    const requirements = this.props.category.signupRequirements;

    let teamMembers = null;
    if (requirements.minTeamSize) {
      const individuals = new Array(requirements.maxTeamSize).fill(null).map((x, index) =>
        <TextInput
          key={index}
          style={styles.textInput}
          placeholder="Mike Lambert"
          />
      );
      teamMembers = <Card>
        <Text>Team Members:</Text>
        {individuals}
      </Card>;
    }

    let teamName = null;
    if (requirements.needsTeamName) {
      teamName = <Card>
        <Text>Team Name:</Text>
        <TextInput
          style={styles.textInput}
          placeholder="A and B"
          />
      </Card>;
    }

    return <View>
      {teamMembers}
      {teamName}
      <Card>
      <GiftedForm
      scrollEnabled={false}
        formName='signupForm' // GiftedForm instances that use the same name will also share the same states

        openModal={(route) => {
          navigator.push(route); // The ModalWidget will be opened using this method. Tested with ExNavigator
        }}

        clearOnClose={false} // delete the values of the form when unmounted

        formStyles={{
          containerView: {backgroundColor: 'transparent'},
          TextInputWidget: {
            rowContainer: Object.assign({}, defaultFont, {
              backgroundColor: 'transparent',
              borderColor: purpleColors[0],
            }),
            textInputTitleInline: defaultFont,
            textInputTitle: defaultFont,
            textInput: Object.assign({}, defaultFont, {backgroundColor: purpleColors[1]}),
            textInputInline: Object.assign({}, defaultFont, {}),
          },
          SubmitWidget: {
            submitButton: {
              backgroundColor: purpleColors[3],
            },
          },
        }}

        defaults={{
          /*
          username: 'Farid',
          'gender{M}': true,
          password: 'abcdefg',
          country: 'FR',
          birthday: new Date(((new Date()).getFullYear() - 18)+''),
          */
        }}

        validators={{
          fullName: {
            title: 'Full name',
            validate: [{
              validator: 'isLength',
              arguments: [1, 23],
              message: '{TITLE} must be between {ARGS[0]} and {ARGS[1]} characters'
            }]
          },
          username: {
            title: 'Username',
            validate: [{
              validator: 'isLength',
              arguments: [3, 16],
              message: '{TITLE} must be between {ARGS[0]} and {ARGS[1]} characters'
            },{
              validator: 'matches',
              arguments: /^[a-zA-Z0-9]*$/,
              message: '{TITLE} can contains only alphanumeric characters'
            }]
          },
        }}
      >

        <GiftedForm.TextInputWidget
          name='fullName' // mandatory
          title='Full name'

          placeholderTextColor="rgba(255, 255, 255, 0.5)"
          keyboardAppearance="dark"

          placeholder='Marco Polo'
          clearButtonMode='while-editing'
        />


        <GiftedForm.TextInputWidget
          name='username'
          title='Username'

          placeholderTextColor="rgba(255, 255, 255, 0.5)"

          placeholder='MarcoPolo'
          clearButtonMode='while-editing'

          onTextInputFocus={(currentText = '') => {
            if (!currentText) {
              let fullName = GiftedFormManager.getValue('signupForm', 'fullName');
              if (fullName) {
                return fullName.replace(/[^a-zA-Z0-9-_]/g, '');
              }
            }
            return currentText;
          }}
        />

        <GiftedForm.SeparatorWidget />

        <GiftedForm.SubmitWidget
          title='Sign up'
          onSubmit={(isValid, values, validationResults, postSubmit = null, modalNavigator = null) => {
            if (isValid === true) {
              // prepare object
              values.gender = values.gender[0];

              /* Implement the request to your server using values variable
              ** then you can do:
              ** postSubmit(); // disable the loader
              ** postSubmit(['An error occurred, please try again']); // disable the loader and display an error message
              ** postSubmit(['Username already taken', 'Email already taken']); // disable the loader and display an error message
              ** GiftedFormManager.reset('signupForm'); // clear the states of the form manually. 'signupForm' is the formName used
              */
            }
          }}

        />

        <GiftedForm.NoticeWidget
          title='By signing up, you agree to the Terms of Service and Privacy Policity.'
        />

        <GiftedForm.HiddenWidget name='tos' value={true} />

      </GiftedForm>
      </Card>

      <Button
        caption="Register"
        style={{margin: 10}}
        onPress={this.props.onRegisterSubmit}
        />
    </View>;
  }
}

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
  textInput: {
    height: 30,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    marginTop: 5,
  },
});
