/**
 * Copyright 2016 DanceDeets.
 */
import * as React from 'react';
import { getAddress, getPosition } from '../util/geo';

interface Position {
  coords: {
    latitude: number;
    longitude: number;
  };
}

interface PositionProviderProps {
  renderWithPosition: (position: Position | null) => React.ReactElement;
}

interface PositionProviderState {
  position: Position | null;
}

export default class PositionProvider extends React.Component<
  PositionProviderProps,
  PositionProviderState
> {
  constructor(props: PositionProviderProps) {
    super(props);
    this.state = { position: null };
  }

  componentWillMount(): void {
    this.loadLocation();
  }

  async loadLocation(): Promise<void> {
    try {
      const position = await getPosition();
      this.setState({ position });
    } catch (e) {
      console.log('Error fetching user position:', e);
    }
  }

  render(): React.ReactElement {
    return this.props.renderWithPosition(this.state.position);
  }
}
