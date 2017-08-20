/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';

export default class Card extends React.Component {
  props: {
    children?: Array<React.Element<*>>,
    className?: string,
    newStyle?: boolean,
  };

  render() {
    const { children, className, newStyle, ...otherProps } = this.props;
    const realClassName = this.props.newStyle ? 'new-card' : 'card';
    return (
      <div className={`${className || ''} ${realClassName}`} {...otherProps}>
        {children}
      </div>
    );
  }
}
