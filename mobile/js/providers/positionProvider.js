/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */
import * as React from 'react';
import { getAddress, getPosition } from '../util/geo';

type Position = Object;

export default class PositionProvider extends React.Component {
  props: {
    renderWithPosition: (position: ?Position) => React.Element<*>,
  };
  state: {
    position: ?Position,
  };

  constructor(props: Object) {
    super(props);
    this.state = { position: null };
  }

  componentWillMount() {
    this.loadLocation();
  }

  async loadLocation() {
    try {
      const position = await getPosition();
      this.setState({ position });
    } catch (e) {
      console.log('Error fetching user position:', e);
    }
  }

  render() {
    return this.props.renderWithPosition(this.state.position);
  }
}
