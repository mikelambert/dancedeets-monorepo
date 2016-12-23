/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';

export default class Link extends React.Component {
  props: {
    children?: any;
    style?: any;
  }
  render() {
    const { children, style, ...otherProps } = this.props;
    const fullStyle = { cursor: 'pointer', ...style };
    return <div style={fullStyle} {...otherProps}>{children}</div>;
  }
}
