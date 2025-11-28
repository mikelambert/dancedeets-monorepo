/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { injectIntl } from 'react-intl';
import { connect } from 'react-redux';
import { GiftedForm } from 'react-native-gifted-form';
import type {
  NavigationAction,
  NavigationRoute,
  NavigationScreenProp,
} from 'react-navigation/src/TypeDefinition';
import { MyGiftedForm, MyGiftedSubmitWidget } from '../ui';
import type { User } from '../actions/types';
import type { BattleCategory, BattleEvent } from './models';
import { eventRegister } from '../api/dancedeets';

interface CategorySignupScreenProps {
  user?: User;
  battle: BattleEvent;
  category: BattleCategory;

  // Self-managed props
  navigation: NavigationScreenProp<any>;
}

interface CategorySignupScreenState {
  values: { [key: string]: any };
}

class _CategorySignupScreen extends React.Component<
  CategorySignupScreenProps,
  CategorySignupScreenState
> {
  constructor(props: CategorySignupScreenProps) {
    super(props);
    const state: CategorySignupScreenState = {
      values: {
        ...this.teamDefaults(),
        team_name: '',
      },
    };
    if (this.props.user) {
      state.values.dancer_name_1 = this.props.user.profile.name;
    }
    this.state = state;
    this.handleValueChange = this.handleValueChange.bind(this);
  }

  computeDefaultTeamName() {
    const dancers = [];
    let index = 1;
    while (this.state.values[`dancer_name_${index}`]) {
      dancers.push(this.state.values[`dancer_name_${index}`]);
      index += 1;
    }
    return dancers.join(' and ');
  }

  teamIndices() {
    const { rules } = this.props.category;
    const zeroToN = Array.from(Array(rules.teamSize).keys());
    return zeroToN;
  }

  teamDefaults() {
    const defaults: { [key: string]: string } = {};
    this.teamIndices().forEach(index => {
      defaults[`dancer_name_${index + 1}`] = '';
    });
    return defaults;
  }

  teamWidgets() {
    return this.teamIndices().map(index => (
      <GiftedForm.TextInputWidget
        key={index}
        name={`dancer_name_${index + 1}`}
        title={`Dancer ${index + 1}`}
        placeholder=""
        {...this.textInputProps()}
      />
    ));
  }

  teamValidators() {
    const validators: {
      [key: string]: { title: string; validate: any[] };
    } = {};
    this.teamIndices().forEach(index => {
      validators[`dancer_name_${index + 1}`] = {
        title: `Dancer ${index + 1}`,
        validate: [],
      };
    });
    return validators;
  }

  textInputProps() {
    return {
      placeholderTextColor: 'rgba(255, 255, 255, 0.5)',
      keyboardAppearance: 'dark' as const,

      clearButtonMode: 'while-editing' as const,
      underlined: true,
      autoCorrect: false,
      autoCapitalize: 'words' as const,
    };
  }

  fakeNavigator() {
    return {
      pop: () => this.props.navigation.goBack(),
    };
  }

  handleValueChange(values: { [key: string]: any }) {
    this.setState({ values });
  }

  render() {
    const { rules } = this.props.category;

    let teamMember1: React.ReactNode[] = [];
    let teamMembers = rules.teamSize ? this.teamWidgets() : null;
    if (this.props.user) {
      teamMember1 = [
        <GiftedForm.HiddenWidget
          key="hidden_0"
          name="dancer_id_1"
          value={this.props.user.profile.id}
        />,
        <GiftedForm.TextInputWidget
          key={0}
          name="dancer_name_1" // mandatory
          title="Dancer 1 (You)"
          validationImage={false}
          {...this.textInputProps()}
        />,
      ];
      teamMembers = teamMembers ? teamMembers.slice(1) : null;
    }

    let teamName = null;
    if (rules.needsTeamName) {
      teamName = (
        <GiftedForm.TextInputWidget
          name="team_name" // mandatory
          title="Team Name"
          placeholder={this.computeDefaultTeamName()}
          {...this.textInputProps()}
        />
      );
    }
    return (
      <MyGiftedForm
        navigator={this.fakeNavigator()}
        scrollEnabled={false}
        formName="signupForm" // GiftedForm instances that use the same name will also share the same states
        openModal={(route: any) => this.props.navigation.navigate(route)}
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
          onSubmit={async (
            isValid: boolean,
            values: { [key: string]: any },
            validationResults: any,
            postSubmit: ((errors?: string[]) => void) | null = null,
            modalNavigator: any = null
          ) => {
            if (isValid === true) {
              // prepare object

              /* Implement the request to your server using values variable
            ** then you can do:
            ** postSubmit(); // disable the loader
            ** postSubmit(['An error occurred, please try again']); // disable the loader and display an error message
            ** postSubmit(['Username already taken', 'Email already taken']); // disable the loader and display an error message
            ** GiftedFormManager.reset('signupForm'); // clear the states of the form manually. 'signupForm' is the formName used
            */
              const newValues = { ...values };
              if (!newValues.team_name) {
                newValues.team_name = this.computeDefaultTeamName();
              }
              const result = await eventRegister(
                this.props.battle.id,
                this.props.category.id,
                { team: newValues }
              );
              console.log('register result is', result);
              if (postSubmit) {
                postSubmit();
              }
              // Do we want this?
              // this.props.onRegisterSubmit();
              if (modalNavigator) {
                modalNavigator.pop();
              }
            }
          }}
        />
      </MyGiftedForm>
    );
  }
}
const CategorySignupScreen = connect((state: any) => ({
  user: state.user.userData,
}))(injectIntl(_CategorySignupScreen));

export default CategorySignupScreen;
