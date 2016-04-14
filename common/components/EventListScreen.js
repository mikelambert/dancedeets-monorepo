import React, { View, Text, PropTypes, StyleSheet } from 'react-native'

import NavButton from './NavButton'
import MainFrame from '../mainFrame'

const EventListScreen = (props) => {
	return (
		<View style={styles.container}>
            <MainFrame onEventSelected={props.onEventSelected}/>
		</View>
	)
}

EventListScreen.propTypes = {
	onEventSelected: PropTypes.func.isRequired
}

const styles = StyleSheet.create({
	container: {
		flex: 1,
		backgroundColor: '#2F9CB2',
	},
})

export default EventListScreen