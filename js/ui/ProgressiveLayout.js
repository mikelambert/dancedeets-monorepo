/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  ListView,
} from 'react-native';

type Props = {
  children?: any;
};

export default class ProgressiveLayout extends React.Component {
  state: {
    dataSource: ListView.DataSource,
  };

  props: Props;

  constructor(props: Props) {
    super(props);
    const dataSource = new ListView.DataSource({
      rowHasChanged: (row1, row2) => row1 !== row2,
    });
    this.state = {dataSource};
    this.state = this._getNewState(props);
    (this: any)._renderRow = this._renderRow.bind(this);
  }

  _getNewState(props: Props) {
    return {
      dataSource: this.state.dataSource.cloneWithRows(props.children),
    };
  }

  componentWillReceiveProps(nextProps: Props) {
    this.setState(this._getNewState(nextProps));
  }

  _renderRow(elem: number) {
    return elem;
  }

  render() {
    const {children, ...otherProps} = this.props;
    return <ListView
      dataSource={this.state.dataSource}
      renderRow={this._renderRow}
      initialListSize={1}
      pageSize={1}
      scrollRenderAheadDistance={10000}
      indicatorStyle="white"
      {...otherProps}
    />;
  }
}
