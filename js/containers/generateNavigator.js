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

// My overrides
import { NavigationHeaderTitle } from '../react-navigation';
import { gradientBottom, gradientTop } from '../Colors';
import { navigatePush, navigatePop, navigateSwap } from '../actions';
import ShareEventIcon from './ShareEventIcon';
import { getNamedState } from '../reducers/navigation';
import type { ThunkAction, Dispatch } from '../actions/types';
import type {
	NavigationRoute,
	NavigationScene,
	NavigationState,
} from 'NavigationTypeDefinition';

const {
	AnimatedView: NavigationAnimatedView,
	Card: NavigationCard,
	Header: NavigationHeader
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

class AppContainer extends React.Component {
	props: AppContainerProps & Navigatable & CallingProps;

	constructor(props) {
		super(props);
		(this: any).renderOverlay = this.renderOverlay.bind(this);
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

	renderOverlay(props) {
		return <GradientBar style={styles.navHeader}>
			<NavigationHeader
				style={{backgroundColor: 'transparent', borderBottomWidth: 0}}
				{...props}
				renderLeftComponent={this.renderLeft}
				renderTitleComponent={this.renderTitle}
				renderRightComponent={this.renderRight}
        // Use this.props here, instead of passed-in props
        onNavigateBack={this.props.onBack}
			/>
		</GradientBar>;
	}

	render() {
		let { navigationState, onBack } = this.props;

		return (

			// Note that we are not using a NavigationRootContainer here because Redux is handling
			// the reduction of our state for us. Instead, we grab the navigationState we have in
			// our Redux store and pass it directly to the <NavigationAnimatedView />.
      //
      // In RN 0.30, convert to NavigationTransitioner:
      // https://github.com/jmurzy/react-native/commit/e040531b6fb75243f72611acf998300b32ca111e
			<NavigationAnimatedView
				navigationState={navigationState}
				style={styles.outerContainer}
				onBack={onBack}
				renderOverlay={this.renderOverlay}
				renderScene={props => (
					// Again, we pass our navigationState from the Redux store to <NavigationCard />.
					// Finally, we'll render out our scene based on navigationState in _renderScene().
					<NavigationCard
						{...props}
						key={props.scene.route.key}
						style={{marginTop: APPBAR_HEIGHT + STATUSBAR_HEIGHT}}
						renderScene={({scene}) => this.props.renderScene(scene, this.props)}
					/>
				)}
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
});
