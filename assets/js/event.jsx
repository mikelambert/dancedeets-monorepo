/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';

class Card extends React.Component {
  render() {
    return <div style={{borderRadius: '15px', backgroundColor: '#4C4D81', padding: '10px'}}>
    {this.props.children}
    </div>;
  }
}

export default class EventPage extends React.Component {
  render() {
    return <Card>{this.props.event.name}</Card>;
  }
}

module.exports = EventPage;
