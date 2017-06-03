/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React, { Element, PropTypes } from 'react';
import {
  Image,
  Platform,
  StyleSheet,
  TouchableOpacity,
  View,
} from 'react-native';
import { connect } from 'react-redux';
import { injectIntl, intlShape } from 'react-intl';
import { hardwareBackPress } from 'react-native-back-android';
import type {
  NavigationRoute,
  NavigationSceneRendererProps,
  NavigationState,
} from 'react-navigation/src/TypeDefinition';
import { CardStack, Header } from 'react-navigation';
import { navigatePush, navigatePop, navigateSwap } from '../actions';
import ShareEventIcon from './ShareEventIcon';
import { getNamedState } from '../reducers/navigation';
import type { ThunkAction, Dispatch } from '../actions/types';
import { semiNormalize, Text } from '../ui';
import { gradientTop, purpleColors } from '../Colors';

// These are basically copied from Header.js.
// But we made it shorter on Android for the more compact display
const APPBAR_HEIGHT = Platform.OS === 'ios' ? 44 : 46;
const STATUSBAR_HEIGHT = Platform.OS === 'ios' ? 20 : 0;


  renderLeft(props) {
    if (!props.scene.index) {
      return null;
    }
    const icon = Platform.OS === 'ios'
      ? require('./navbar-icons/back-ios.png')
      : require('./navbar-icons/back-android.png');
    return (
      <TouchableOpacity
        style={styles.centeredContainer}
        onPress={props.onNavigateBack}
      >
        <Image style={{ height: 18, width: 18 }} source={icon} />
      </TouchableOpacity>
    );
  }

  renderRight(props) {
    if (props.scene.route.event) {
      return (
        <View style={styles.centeredContainer}>
          <ShareEventIcon event={props.scene.route.event} />
        </View>
      );
    }
    return null;
  }

        style={[
          styles.navHeader,
          { backgroundColor: gradientTop, borderBottomWidth: 0 },
        ]}

        cardStyle={{
          backgroundColor: purpleColors[4],
          marginTop: APPBAR_HEIGHT + STATUSBAR_HEIGHT,
        }}
      />

const styles = StyleSheet.create({
  outerContainer: {
    flex: 1,
    backgroundColor: 'black',
  },
  container: {
    flex: 1,
  },
  // These are basically copied from Header.js
  navHeader: {
    alignItems: 'center',
    elevation: 1,
    flexDirection: 'row',
    height: APPBAR_HEIGHT + STATUSBAR_HEIGHT,
    justifyContent: 'flex-start',
    left: 0,
    marginBottom: 16, // This is needed for elevation shadow
    position: 'absolute',
    right: 0,
    top: 0,
  },
  centeredContainer: {
    flex: 1,
    justifyContent: 'center',
    marginLeft: 10,
    marginRight: 10,
  },
  title: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 16,
  },
  titleText: {
    flex: 1,
    fontSize: semiNormalize(18),
    fontWeight: '500',
    color: 'white',
    textAlign: Platform.OS === 'ios' ? 'center' : 'left',
  },
});
