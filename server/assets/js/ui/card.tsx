/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  newStyle?: boolean;
}

export default class Card extends React.Component<CardProps> {
  render(): React.ReactNode {
    const { children, className, newStyle, ...otherProps } = this.props;
    const realClassName = this.props.newStyle ? 'new-card' : 'card';
    return (
      <div className={`${className || ''} ${realClassName}`} {...otherProps}>
        {children}
      </div>
    );
  }
}
