/**
 * Copyright 2016 DanceDeets.
 *
 * React Navigation v6 Battle screens
 */

import * as React from 'react';
import { createStackNavigator, StackScreenProps } from '@react-navigation/stack';
import { useIntl, defineMessages } from 'react-intl';
import { BattleSelector } from '../../event_signups/views';
import { TrackFirebase } from '../../firestack';
import CategorySignupScreen from '../../event_signups/categorySignupScreen';
import CategoryView from '../../event_signups/categoryView';
import BattleEventView from '../../event_signups/battleEventView';
import BattleEventHostView from '../../event_signups/battleEventHostView';
import BattleHostCategoryView from '../../event_signups/battleHostCategoryView';
import { eventUnregister } from '../../api/dancedeets';
import { gradientTop } from '../../Colors';

const messages = defineMessages({
  battleSignups: {
    id: 'battle.signups',
    defaultMessage: 'Battle Signups',
    description: 'Title for battle signups screen',
  },
});

// Type definitions for navigation
type BattleStackParamList = {
  BattleSelector: { battleId: string };
  BattleSignups: { battleId: string };
  Category: { battleId: string; categoryId: string };
  Register: { battleId: string; categoryId: string };
  BattleHostView: { battleId: string };
  BattleHostCategory: { battleId: string; categoryId: string };
};

const Stack = createStackNavigator<BattleStackParamList>();

// Helper functions
function onRegister(
  navigation: any,
  battleId: string,
  category: any
) {
  navigation.navigate('Register', {
    battleId,
    categoryId: category.id,
  });
}

async function onUnregister(battleId: string, category: any, teamToDelete: any) {
  const [teamKey] = Object.entries(category.signups || {}).filter(
    ([key, team]) => team === teamToDelete
  )[0];
  await eventUnregister(battleId, category.id, teamKey);
}

// Battle Selector Screen
interface BattleSelectorScreenProps extends StackScreenProps<BattleStackParamList, 'BattleSelector'> {}

function BattleSelectorScreen({ navigation, route }: BattleSelectorScreenProps) {
  const { battleId } = route.params;
  return (
    <BattleSelector
      onBattleSelected={() => navigation.navigate('BattleSignups', { battleId })}
      onBattleHostSelected={() => navigation.navigate('BattleHostView', { battleId })}
    />
  );
}

// Battle Signups Screen
interface BattleSignupsScreenProps extends StackScreenProps<BattleStackParamList, 'BattleSignups'> {}

function BattleSignupsScreen({ navigation, route }: BattleSignupsScreenProps) {
  const { battleId } = route.params;
  return (
    <TrackFirebase
      path={`events/${battleId}`}
      renderContents={(battleEvent: any) => (
        <BattleEventView
          battleEvent={battleEvent}
          onSelected={(selectedCategory: any) => {
            navigation.navigate('Category', {
              battleId,
              categoryId: selectedCategory.id,
            });
          }}
          onRegister={(category: any) => onRegister(navigation, battleId, category)}
          onUnregister={(category: any, teamToDelete: any) =>
            onUnregister(battleId, category, teamToDelete)}
        />
      )}
    />
  );
}

// Register Screen
interface RegisterScreenProps extends StackScreenProps<BattleStackParamList, 'Register'> {}

function RegisterScreen({ navigation, route }: RegisterScreenProps) {
  const { battleId, categoryId } = route.params;
  return (
    <TrackFirebase
      path={`events/${battleId}`}
      renderContents={(battleEvent: any) => {
        const category = battleEvent.categories[categoryId];
        return (
          <CategorySignupScreen
            battle={battleEvent}
            category={category}
            navigation={navigation}
          />
        );
      }}
    />
  );
}

// Category Screen
interface CategoryScreenProps extends StackScreenProps<BattleStackParamList, 'Category'> {}

function CategoryScreen({ navigation, route }: CategoryScreenProps) {
  const { battleId, categoryId } = route.params;
  return (
    <TrackFirebase
      path={`events/${battleId}`}
      renderContents={(battleEvent: any) => {
        const category = battleEvent.categories[categoryId];
        return (
          <CategoryView
            category={category}
            onRegister={(category2: any) => onRegister(navigation, battleId, category2)}
            onUnregister={(category2: any, teamToDelete: any) =>
              onUnregister(battleId, category2, teamToDelete)}
          />
        );
      }}
    />
  );
}

// Battle Host Screen
interface BattleHostScreenProps extends StackScreenProps<BattleStackParamList, 'BattleHostView'> {}

function BattleHostScreen({ navigation, route }: BattleHostScreenProps) {
  const { battleId } = route.params;
  return (
    <TrackFirebase
      path={`events/${battleId}`}
      renderContents={(battleEvent: any) => (
        <BattleEventHostView
          battleEvent={battleEvent}
          onSelected={(selectedCategory: any) => {
            navigation.navigate('BattleHostCategory', {
              battleId,
              categoryId: selectedCategory.id,
            });
          }}
        />
      )}
    />
  );
}

// Battle Host Category Screen
interface BattleHostCategoryProps extends StackScreenProps<BattleStackParamList, 'BattleHostCategory'> {}

function BattleHostCategoryScreen({ route }: BattleHostCategoryProps) {
  const { battleId, categoryId } = route.params;
  return (
    <TrackFirebase
      path={`events/${battleId}`}
      renderContents={(battleEvent: any) => {
        const category = battleEvent.categories[categoryId];
        return <BattleHostCategoryView category={category} />;
      }}
    />
  );
}

// Main Battle Screens Navigator
export function BattleScreensNavigator() {
  const intl = useIntl();

  return (
    <Stack.Navigator
      id="BattleStack"
      screenOptions={{
        headerTintColor: 'white',
        headerStyle: {
          backgroundColor: gradientTop,
        },
        cardStyle: {
          backgroundColor: 'black',
        },
      }}
    >
      <Stack.Screen
        name="BattleSelector"
        component={BattleSelectorScreen}
        options={{
          title: intl.formatMessage(messages.battleSignups),
        }}
      />
      <Stack.Screen
        name="BattleSignups"
        component={BattleSignupsScreen}
        options={({ route }) => ({
          title: `${route.params.battleId} Registration`,
        })}
      />
      <Stack.Screen
        name="Category"
        component={CategoryScreen}
        options={{
          title: 'Category',
        }}
      />
      <Stack.Screen
        name="Register"
        component={RegisterScreen}
        options={{
          title: 'Register',
        }}
      />
      <Stack.Screen
        name="BattleHostView"
        component={BattleHostScreen}
        options={({ route }) => ({
          title: `${route.params.battleId} MC Host View`,
        })}
      />
      <Stack.Screen
        name="BattleHostCategory"
        component={BattleHostCategoryScreen}
        options={{
          title: 'Host Category',
        }}
      />
    </Stack.Navigator>
  );
}
