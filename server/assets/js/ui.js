/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';

export class Card extends React.Component {
  props: {
    children?: Array<React.Element<*>>;
    className?: string;
  }

  render() {
    const { children, className, ...otherProps } = this.props;
    return (<div className={`card ${className || ''}`} {...otherProps} >
      {children}
    </div>);
  }
}
