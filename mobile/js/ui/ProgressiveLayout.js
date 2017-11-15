/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { ListView } from 'react-native';

type Props = {
  children: React.Node,
};

export default class ProgressiveLayout extends React.Component<
  Props,
  {
    dataSource: ListView.DataSource,
  }
> {
  constructor(props: Props) {
    super(props);
    const dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
    });
    this.state = { dataSource };
    this.state = this.getNewState(props);
  }

  componentWillReceiveProps(nextProps: Props) {
    this.setState(this.getNewState(nextProps));
  }

  getNewState(props: Props) {
    return {
      dataSource: this.state.dataSource.cloneWithRows(props.children),
    };
  }

  renderRow(elem: number) {
    return elem;
  }

  render() {
    const { children, ...otherProps } = this.props;
    return (
      <ListView
        dataSource={this.state.dataSource}
        renderRow={this.renderRow}
        initialListSize={1}
        pageSize={1}
        scrollRenderAheadDistance={10000}
        indicatorStyle="white"
        {...otherProps}
      />
    );
  }
}
