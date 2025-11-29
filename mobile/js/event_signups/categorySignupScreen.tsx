/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { useSelector } from 'react-redux';
import { GiftedForm } from 'react-native-gifted-form';
import type {
  NavigationAction,
  NavigationRoute,
  NavigationScreenProp,
} from 'react-navigation/src/TypeDefinition';
import { MyGiftedForm, MyGiftedSubmitWidget } from '../ui';
import type { User, RootState } from '../actions/types';
import type { BattleCategory, BattleEvent } from './models';
import { eventRegister } from '../api/dancedeets';

interface CategorySignupScreenProps {
  battle: BattleEvent;
  category: BattleCategory;
  navigation: NavigationScreenProp<any>;
}

function CategorySignupScreen({ battle, category, navigation }: CategorySignupScreenProps) {
  const user = useSelector((state: RootState) => state.user.userData);

  const teamIndices = React.useCallback(() => {
    const { rules } = category;
    const zeroToN = Array.from(Array(rules.teamSize).keys());
    return zeroToN;
  }, [category]);

  const teamDefaults = React.useCallback(() => {
    const defaults: { [key: string]: string } = {};
    teamIndices().forEach(index => {
      defaults[`dancer_name_${index + 1}`] = '';
    });
    return defaults;
  }, [teamIndices]);

  const initialValues = React.useMemo(() => {
    const vals: { [key: string]: any } = {
      ...teamDefaults(),
      team_name: '',
    };
    if (user) {
      vals.dancer_name_1 = user.profile.name;
    }
    return vals;
  }, [teamDefaults, user]);

  const [values, setValues] = React.useState(initialValues);

  const computeDefaultTeamName = React.useCallback(() => {
    const dancers = [];
    let index = 1;
    while (values[`dancer_name_${index}`]) {
      dancers.push(values[`dancer_name_${index}`]);
      index += 1;
    }
    return dancers.join(' and ');
  }, [values]);

  const textInputProps = () => ({
    placeholderTextColor: 'rgba(255, 255, 255, 0.5)',
    keyboardAppearance: 'dark' as const,
    clearButtonMode: 'while-editing' as const,
    underlined: true,
    autoCorrect: false,
    autoCapitalize: 'words' as const,
  });

  const teamWidgets = () => {
    return teamIndices().map(index => (
      <GiftedForm.TextInputWidget
        key={index}
        name={`dancer_name_${index + 1}`}
        title={`Dancer ${index + 1}`}
        placeholder=""
        {...textInputProps()}
      />
    ));
  };

  const teamValidators = () => {
    const validators: {
      [key: string]: { title: string; validate: any[] };
    } = {};
    teamIndices().forEach(index => {
      validators[`dancer_name_${index + 1}`] = {
        title: `Dancer ${index + 1}`,
        validate: [],
      };
    });
    return validators;
  };

  const fakeNavigator = () => ({
    pop: () => navigation.goBack(),
  });

  const handleValueChange = (newValues: { [key: string]: any }) => {
    setValues(newValues);
  };

  const { rules } = category;

  let teamMember1: React.ReactNode[] = [];
  let teamMembers = rules.teamSize ? teamWidgets() : null;
  if (user) {
    teamMember1 = [
      <GiftedForm.HiddenWidget
        key="hidden_0"
        name="dancer_id_1"
        value={user.profile.id}
      />,
      <GiftedForm.TextInputWidget
        key={0}
        name="dancer_name_1"
        title="Dancer 1 (You)"
        validationImage={false}
        {...textInputProps()}
      />,
    ];
    teamMembers = teamMembers ? teamMembers.slice(1) : null;
  }

  let teamName = null;
  if (rules.needsTeamName) {
    teamName = (
      <GiftedForm.TextInputWidget
        name="team_name"
        title="Team Name"
        placeholder={computeDefaultTeamName()}
        {...textInputProps()}
      />
    );
  }

  return (
    <MyGiftedForm
      navigator={fakeNavigator()}
      scrollEnabled={false}
      formName="signupForm"
      openModal={(route: any) => navigation.navigate(route)}
      defaults={values}
      validators={{
        team_name: {
          title: 'Team Name',
          validate: [],
        },
        ...teamValidators(),
      }}
      onValueChange={handleValueChange}
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
          submitValues: { [key: string]: any },
          validationResults: any,
          postSubmit: ((errors?: string[]) => void) | null = null,
          modalNavigator: any = null
        ) => {
          if (isValid === true) {
            const newValues = { ...submitValues };
            if (!newValues.team_name) {
              newValues.team_name = computeDefaultTeamName();
            }
            const result = await eventRegister(
              battle.id,
              category.id,
              { team: newValues }
            );
            console.log('register result is', result);
            if (postSubmit) {
              postSubmit();
            }
            if (modalNavigator) {
              modalNavigator.pop();
            }
          }
        }}
      />
    </MyGiftedForm>
  );
}

export default CategorySignupScreen;
