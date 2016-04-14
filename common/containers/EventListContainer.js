import { connect } from 'react-redux'

import EventListScreen from '../components/EventListScreen'
import { navigatePush } from '../actions'


const mapStateToProps = (state) => {
	return {	
	}
}

const mapDispatchToProps = (dispatch) => {
	return {
		onEventSelected: (event) => {
			dispatch(navigatePush(event.name))
		}
	}
}

export default connect(
	mapStateToProps,
	mapDispatchToProps
)(EventListScreen)