import React, { View, PropTypes, StyleSheet } from 'react-native';

import MainFrame from '../mainFrame';

const EventListScreen = (props) => {
	return (
		<View style={styles.container}>
            <MainFrame onEventSelected={props.onEventSelected}/>
		</View>
	);
};

EventListScreen.propTypes = {
	onEventSelected: PropTypes.func.isRequired
};
export default EventListScreen;

const styles = StyleSheet.create({
	container: {
		flex: 1,
		backgroundColor: '#2F9CB2',
	},
});
