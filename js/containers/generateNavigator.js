/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
	Image,
	NavigationExperimental,
	Platform,
	StyleSheet,
	TouchableOpacity,
	View,
} from 'react-native';
import { connect } from 'react-redux';
import {
  injectIntl,
  intlShape,
} from 'react-intl';
import { gradientTop } from '../Colors';
import { navigatePush, navigatePop, navigateSwap } from '../actions';
import ShareEventIcon from './ShareEventIcon';
import { getNamedState } from '../reducers/navigation';
import type { ThunkAction, Dispatch } from '../actions/types';
import type {
	NavigationRoute,
	NavigationSceneRendererProps,
	NavigationState,
} from 'NavigationTypeDefinition';
import {
	semiNormalize,
	Text,
} from '../ui';
import {
	purpleColors
} from '../Colors';

const {
	CardStack: NavigationCardStack,
	Header: NavigationHeader,
} = NavigationExperimental;


// These are basically copied from NavigationHeader.js.
// But we made it shorter on Android for the more compact display
const APPBAR_HEIGHT = Platform.OS === 'ios' ? 44 : 46;
const STATUSBAR_HEIGHT = Platform.OS === 'ios' ? 20 : 0;

export type Navigatable = {
	onNavigate: (x: NavigationRoute) => ThunkAction;
	onBack: () => ThunkAction;
	onSwap: (key: string, newState: NavigationRoute) => ThunkAction;
	goHome: () => ThunkAction;
};

type NavigatorProps = {
	navigationState: NavigationState,
	intl: intlShape,
};

type CallingProps = {
	renderScene: (scene: NavigationSceneRendererProps, nav: Navigatable) => ReactElement<any>;
};

const NavigationHeaderTitle = ({ children, style, textStyle, viewProps }) => (
  <View style={[ styles.title, style ]} {...viewProps}>
    <Text style={[ styles.titleText, textStyle ]} numberOfLines={1}>{children}</Text>
  </View>
);

class _Navigator extends React.Component {
	props: NavigatorProps & Navigatable & CallingProps;

	constructor(props) {
		super(props);
		(this: any)._renderHeader = this._renderHeader.bind(this);
		(this: any).renderLeft = this.renderLeft.bind(this);
		(this: any).renderTitle = this.renderTitle.bind(this);
		(this: any).renderRight = this.renderRight.bind(this);
	}

	renderLeft(props) {
		if (!props.scene.index) {
			return null;
		}
		const icon = Platform.OS == 'ios' ? require('./navbar-icons/back-ios.png') : require('./navbar-icons/back-android.png');
		return <TouchableOpacity style={styles.centeredContainer} onPress={props.onNavigateBack}>
			<Image style={{height: 18, width: 18}} source={icon} />
		</TouchableOpacity>;
	}

	renderTitle(props) {
		let title = props.scene.route.title;
		if (props.scene.route.message) {
			title = this.props.intl.formatMessage(props.scene.route.message);
		}
		return <NavigationHeaderTitle>
			{title}
		</NavigationHeaderTitle>;
	}

	renderRight(props) {
		if (props.scene.route.event) {
			return <View style={styles.centeredContainer}><ShareEventIcon event={props.scene.route.event} /></View>;
		}
		return null;
	}

	_renderHeader(props) {
		// 0.33: Disable for now, as it doesn't appear to work: <GradientBar style={styles.navHeader}>
		return <NavigationHeader
			{...props}
			style={[styles.navHeader, {backgroundColor: gradientTop, borderBottomWidth: 0}]}
			renderLeftComponent={this.renderLeft}
			renderTitleComponent={this.renderTitle}
			renderRightComponent={this.renderRight}
      // Use this.props here, instead of passed-in props
      onNavigateBack={this.props.onBack}
		/>;
	}

	render() {
		return (
			<NavigationCardStack
				navigationState={this.props.navigationState}
				style={styles.outerContainer}
				onBack={this.props.onBack}
				renderHeader={this._renderHeader}
				renderScene={this.props.renderScene}
				cardStyle={{
					backgroundColor: purpleColors[4],
					marginTop: APPBAR_HEIGHT + STATUSBAR_HEIGHT,
				}}
			/>
		);
	}

  backToHome() {
    this.props.goHome();
  }
}
const Navigator = injectIntl(_Navigator);

export default function(navName: string) {
	return connect(
		state => ({
			navigationState: getNamedState(state.navigationState, navName),
		}),
		(dispatch: Dispatch) => ({
			onNavigate: (destState) => dispatch(navigatePush(navName, destState)),
			goHome: async () => {
				await dispatch(navigatePop(navName));
				await dispatch(navigatePop(navName));
			},
			onBack: () => dispatch(navigatePop(navName)),
			onSwap: (key, newRoute) => dispatch(navigateSwap(navName, key, newRoute)),
		}),
	)(Navigator);
}

const styles = StyleSheet.create({
	outerContainer: {
		flex: 1,
		backgroundColor: 'black',
	},
	container: {
		flex: 1,
	},
	// These are basically copied from NavigationHeader.js
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
    marginHorizontal: 16
  },
  titleText: {
    flex: 1,
    fontSize: semiNormalize(18),
    fontWeight: '500',
    color: 'white',
    textAlign: Platform.OS === 'ios' ? 'center' : 'left'
  }

});
