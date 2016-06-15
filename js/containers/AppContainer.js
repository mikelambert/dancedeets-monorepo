/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React, {
	PropTypes,
} from 'react';
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
import EventListContainer from '../events/list';
import EventPager from '../events/EventPager';
import { navigatePush, navigatePop, navigateSwap, navigateJumpToIndex } from '../actions';
import {
	ZoomableImage,
} from '../ui';
import AddEvents from '../containers/AddEvents';
import ShareEventIcon from './ShareEventIcon';
import { track, trackWithEvent } from '../store/track';

import type { ThunkAction, Dispatch } from '../actions/types';
import type { NavigationParentState, NavigationState } from 'NavigationTypeDefinition';

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

class AppContainer extends React.Component {
	props: {
		navigationState: NavigationParentState,
		onNavigate: (x: NavigationState) => ThunkAction,
		onBack: () => ThunkAction,
		onSwap: (key: string, newState: NavigationState) => ThunkAction,
	};

	constructor(props) {
		super(props);
		(this: any).renderScene = this.renderScene.bind(this);
		(this: any).renderOverlay = this.renderOverlay.bind(this);
	}

	renderLeft(props) {
		if (!props.scene.index) {
			return null;
		}
		const icon = Platform.OS == 'ios' ? require('./navbar-icons/back-ios.png') : require('./navbar-icons/back-android.png');
		return <TouchableOpacity style={styles.centeredContainer} onPress={() => props.onNavigate({type: 'BackAction'})}>
			<Image style={{height: 18, width: 18}} source={icon} />
		</TouchableOpacity>;
	}

	renderTitle(props) {
		return <NavigationHeaderTitle
			textStyle={{color: 'white', fontSize: 24}}
		>
			{props.scene.navigationState.title}
		</NavigationHeaderTitle>;
	}

	renderRight(props) {
		if (props.scene.navigationState.event) {
			return <View style={styles.centeredContainer}><ShareEventIcon event={props.scene.navigationState.event} /></View>;
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
			/>
		</GradientBar>;
	}

	render() {
		let { navigationState, onBack } = this.props;

		return (

			// Note that we are not using a NavigationRootContainer here because Redux is handling
			// the reduction of our state for us. Instead, we grab the navigationState we have in
			// our Redux store and pass it directly to the <NavigationAnimatedView />.
			<NavigationAnimatedView
				navigationState={navigationState}
				style={styles.outerContainer}
				onNavigate={(action) => {
					if (action.type === 'back' || action.type === 'BackAction') {
						onBack();
					}
				}}
				renderOverlay={this.renderOverlay}
				renderScene={props => (
					// Again, we pass our navigationState from the Redux store to <NavigationCard />.
					// Finally, we'll render out our scene based on navigationState in _renderScene().
					<NavigationCard
						{...props}
						key={props.scene.navigationState.key}
						style={{marginTop: APPBAR_HEIGHT + STATUSBAR_HEIGHT}}
						renderScene={this.renderScene}
					/>
				)}
			/>
		);
	}

  backToHome() {
    this.props.goHome();
  }

	renderScene({scene}) {
		const { navigationState } = scene;
		switch (navigationState.key) {
		case 'EventList':
			return <EventListContainer
				onEventSelected={(event)=> {
					trackWithEvent('View Event', event);
					this.props.onNavigate({key: 'EventView', title: event.name, event: event});
				}}
				onAddEventClicked={() => {
					track('Add Event');
					this.props.onNavigate({key: 'AddEvent', title: 'Add Event'});
				}}
			/>;
		case 'EventView':
			return <EventPager
				onEventNavigated={(event)=> {
          console.log('HEYHEYHEYHEYHEY');
					trackWithEvent('View Event', event);
					this.props.onSwap('EventView', {key: 'EventView', title: event.name, event: event});
				}}
				onFlyerSelected={(event)=> {
					trackWithEvent('View Flyer', event);
					this.props.onNavigate({
						key: 'FlyerView',
						title: 'Event Flyer',
						image: event.cover.images[0].source,
						width: event.cover.images[0].width,
						height: event.cover.images[0].height,
					});
				}}
				selectedEvent={navigationState.event}
			/>;
		case 'FlyerView':
			return <ZoomableImage
				url={navigationState.image}
				width={navigationState.width}
				height={navigationState.height}
			/>;
		case 'AddEvent':
			return <AddEvents />;
		}
	}
}

AppContainer.propTypes = {
	navigationState: PropTypes.object,
	onNavigate: PropTypes.func.isRequired,
	onBack: PropTypes.func.isRequired,
	onSwap: PropTypes.func.isRequired,
};

export default connect(
	state => ({
		navigationState: state.navigationState
	}),
	(dispatch: Dispatch) => ({
		onNavigate: (destState) => dispatch(navigatePush(destState)),
    goHome: async () => {
      await dispatch(navigatePop());
      await dispatch(navigatePop());
    },
		onBack: () => dispatch(navigatePop()),
		onSwap: (key, newState) => dispatch(navigateSwap(key, newState)),
	}),
)(AppContainer);


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
