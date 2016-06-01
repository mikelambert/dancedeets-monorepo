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
	NavigationExperimental,
	StyleSheet,
} from 'react-native';
import { connect } from 'react-redux';

// My overrides
import { NavigationHeaderTitle } from '../react-navigation';
import NavigationHeaderBackButton from 'react-native/Libraries/CustomComponents/NavigationExperimental/NavigationHeaderBackButton';

import EventListContainer from '../events/list';
import EventPager from '../events/EventPager';
import { navigatePush, navigatePop } from '../actions';
import {
	Text,
	ZoomableImage,
} from '../ui';
import AddEvents from '../containers/AddEvents';

import type { ThunkAction, Dispatch } from '../actions/types';
import type { NavigationParentState, NavigationState } from 'NavigationTypeDefinition';
import { purpleColors } from '../Colors';
const {
	AnimatedView: NavigationAnimatedView,
	Card: NavigationCard,
	Header: NavigationHeader
} = NavigationExperimental;

class AppContainer extends React.Component {
	props: {
		navigationState: NavigationParentState,
		onNavigate: (x: NavigationState) => ThunkAction,
		onBack: () => ThunkAction,
	};

	constructor(props) {
		super(props);
		(this: any)._renderScene = this._renderScene.bind(this);
	}

	renderLeft(props) {
		return props.scene.index > 0 ? <NavigationHeaderBackButton /> : null;
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
			return <Text>Share</Text>;
		}
		return null;
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
				renderOverlay={props => (
					// Also note that we must explicity pass <NavigationHeader /> an onNavigate prop
					// because we are no longer relying on an onNavigate function being available in
					// the context (something NavigationRootContainer would have given us).
					<NavigationHeader
							style={{backgroundColor: purpleColors[2]}}
              {...props}
              renderLeftComponent={this.renderLeft}
						  renderTitleComponent={this.renderTitle}
						  renderRightComponent={this.renderRight}
					/>
				)}

				renderScene={props => (
					// Again, we pass our navigationState from the Redux store to <NavigationCard />.
					// Finally, we'll render out our scene based on navigationState in _renderScene().
					<NavigationCard
						{...props}
						key={props.scene.navigationState.key}
						style={{marginTop: 63}}
						renderScene={this._renderScene}
					/>
				)}
			/>
		);
	}

	_renderScene({scene}) {
		const { navigationState } = scene;
		switch (navigationState.key) {
		case 'EventList':
			return <EventListContainer
				onEventSelected={(event)=>this.props.onNavigate({key: 'EventView', title: event.name, event: event})}
				onAddEventClicked={()=>this.props.onNavigate({key: 'AddEvent', title: 'Add Event'})}
			/>;
		case 'EventView':
      return <EventPager
				onFlyerSelected={(event)=>this.props.onNavigate({
          key: 'FlyerView',
          image: event.cover.images[0].source,
					width: event.cover.images[0].width,
					height: event.cover.images[0].height,
        })}
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
	onBack: PropTypes.func.isRequired
};

export default connect(
	state => ({
		navigationState: state.navigationState
	}),
	(dispatch: Dispatch) => ({
		onNavigate: (destState) => dispatch(navigatePush(destState)),
		onBack: () => dispatch(navigatePop())
	}),
)(AppContainer);


const styles = StyleSheet.create({
	outerContainer: {
		flex: 1
	},
	container: {
		flex: 1
	}
});
