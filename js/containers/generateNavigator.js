/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
	Easing,
	Image,
	NavigationExperimental,
	Platform,
	StyleSheet,
	Text,
	TouchableOpacity,
	View,
} from 'react-native';
import { connect } from 'react-redux';

import { gradientBottom, gradientTop } from '../Colors';
import { navigatePush, navigatePop, navigateSwap } from '../actions';
import ShareEventIcon from './ShareEventIcon';
import { getNamedState } from '../reducers/navigation';
import type { ThunkAction, Dispatch } from '../actions/types';
import type {
	NavigationRoute,
	NavigationScene,
	NavigationState,
	NavigationTransitionProps,
	NavigationTransitionSpec,
} from 'NavigationTypeDefinition';

const {
	CardStack: NavigationCardStack,
	Card: NavigationCard,
	Header: NavigationHeader,
	Transitioner: NavigationTransitioner,
} = NavigationExperimental;
import LinearGradient from 'react-native-linear-gradient';


// These are basically copied from NavigationHeader.js
const APPBAR_HEIGHT = Platform.OS === 'ios' ? 44 : 56;
const STATUSBAR_HEIGHT = Platform.OS === 'ios' ? 20 : 0;

class GradientBar extends React.Component {
	render() {
		return <LinearGradient
			start={[0.0, 0.0]} end={[0.0, 1]}
			colors={[gradientBottom, gradientTop]}
			style={this.props.style}>
			{this.props.children}
		</LinearGradient>;
	}
}

type Navigatable = {
	onNavigate: (x: NavigationRoute) => ThunkAction;
	onBack: () => ThunkAction;
	onSwap: (key: string, newState: NavigationRoute) => ThunkAction;
	goHome: () => ThunkAction;
};

type AppContainerProps = {
	navigationState: NavigationState,
};

type CallingProps = {
	renderScene: (scene: NavigationScene, nav: Navigatable) => React.Component;
};

const NavigationHeaderTitle = ({ children, style, textStyle, viewProps }) => (
  <View style={[ styles.title, style ]} {...viewProps}>
    <Text style={[ styles.titleText, textStyle ]} numberOfLines={1}>{children}</Text>
  </View>
);

class AppContainer extends React.Component {
	props: AppContainerProps & Navigatable & CallingProps;

	constructor(props) {
		super(props);
		(this: any)._renderScene = this._renderScene.bind(this);
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
		return <NavigationHeaderTitle
			textStyle={{color: 'white', fontSize: 24}}
		>
			{props.scene.route.title}
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

	_renderScene(props) {
		// Again, we pass our navigationState from the Redux store to <NavigationCard />.
		// Finally, we'll render out our scene based on navigationState in _renderScene().
		return <NavigationCard
			{...props}
			key={props.scene.route.key}
			style={{marginTop: APPBAR_HEIGHT + STATUSBAR_HEIGHT}}
			renderScene={({scene}) => this.props.renderScene(scene, this.props)}
		/>;
	}

	render() {
		return (
			<NavigationCardStack
				navigationState={this.props.navigationState}
				style={styles.outerContainer}
				onBack={this.props.onBack}
				renderHeader={this._renderHeader}
				renderScene={this._renderScene}
			/>
		);
	}

  backToHome() {
    this.props.goHome();
  }
}

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
			onSwap: (key, newState) => dispatch(navigateSwap(navName, key, newState)),
		}),
	)(AppContainer);
}

const styles = StyleSheet.create({
	outerContainer: {
		flex: 1
	},
	container: {
		flex: 1
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
    fontSize: 18,
    fontWeight: '500',
    color: 'rgba(0, 0, 0, .9)',
    textAlign: Platform.OS === 'ios' ? 'center' : 'left'
  }

});
