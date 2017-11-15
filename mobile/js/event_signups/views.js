/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import {
  Animated,
  Dimensions,
  Image,
  StyleSheet,
  TouchableHighlight,
  View,
} from 'react-native';
import { injectIntl, defineMessages } from 'react-intl';
import { connect } from 'react-redux';
import { GiftedForm } from 'react-native-gifted-form';
import type {
  NavigationRoute,
  NavigationScene,
  NavigationSceneRendererProps,
  NavigationState,
} from 'react-navigation/src/TypeDefinition';
import { track } from '../store/track';
import {
  Button,
  Card,
  HorizontalView,
  MyGiftedForm,
  MyGiftedSubmitWidget,
  normalize,
  ProportionalImage,
  semiNormalize,
  Text,
} from '../ui';
import { purpleColors, yellowColors } from '../Colors';
import type { Dispatch, User } from '../actions/types';
import { categoryDisplayName } from './models';
import type { BattleCategory, BattleEvent, Signup } from './models';
import { eventRegister, eventUnregister } from '../api/dancedeets';
import { TrackFirebase } from '../firestack';
import CategorySignupScreen from './categorySignupScreen';
import CategoryView from './categoryView';
import BattleEventView from './battleEventView';
import BattleEventHostView from './battleEventHostView';
import BattleHostCategoryView from './battleHostCategoryView';

export class BattleSelector extends React.Component<{
  onBattleSelected: (battleId: string) => void,
  onBattleHostSelected: (battleId: string) => void,
}> {
  render() {
    const battleId = 'justeDebout';
    return (
      <HorizontalView style={{ alignItems: 'center' }}>
        <Text>{battleId}</Text>
        <Button
          onPress={() => this.props.onBattleSelected(battleId)}
          caption="Dancer"
        />
        <Button
          onPress={() => this.props.onBattleHostSelected(battleId)}
          caption="Host"
        />
      </HorizontalView>
    );
  }
}

const checkSize = 20;
const checkMargin = 10;
const styles = StyleSheet.create({
  container: {},
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
});
