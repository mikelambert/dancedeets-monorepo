import { connect } from 'react-redux'

import EventListScreen from '../components/EventListScreen'
import { navigatePush } from '../actions'


const mapStateToProps = (state) => {
	return {	
	}
}

const mapDispatchToProps = (dispatch) => {
	return {
		onEventSelected: () => {
			dispatch(navigatePush('EventView'))
		}
	}
}

export default connect(
	mapStateToProps,
	mapDispatchToProps
)(EventListScreen)