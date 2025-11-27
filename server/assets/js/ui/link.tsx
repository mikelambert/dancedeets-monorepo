/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';

interface LinkProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export default class Link extends React.Component<LinkProps> {
  render(): React.ReactNode {
    const { children, style, ...otherProps } = this.props;
    const fullStyle: React.CSSProperties = { cursor: 'pointer', ...style };
    return (
      <div style={fullStyle} {...otherProps}>
        {children}
      </div>
    );
  }
}
