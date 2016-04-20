/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import { connect } from 'react-redux';
import React, { View, PropTypes, StyleSheet } from 'react-native';
import { navigatePush } from '../actions';
import MainFrame from '../mainFrame';

const mapStateToProps = (state) => {
    return {
    };
};

const mapDispatchToProps = (dispatch) => {
    return {
        onEventSelected: (event) => {
            dispatch(navigatePush({key: 'Event View', title: event.name}));
        }
    };
};

const EventListContainer = (props) => {
    return (
        <View style={styles.container}>
            <MainFrame onEventSelected={props.onEventSelected}/>
        </View>
    );
};

EventListContainer.propTypes = {
    onEventSelected: PropTypes.func.isRequired
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(EventListContainer);


const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#2F9CB2',
    },
});


