/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';

import { AmpImage } from './ampImage';
import type { RequiredImage } from './ampImage';

export default class ImagePrefix extends React.Component {
  props: {
    icon?: number, // aka required package
    iconName?: string,
    className?: string,
    amp?: boolean,
    children?: Array<React.Element<*>>,
  };

  render() {
    if (!this.props.icon && !this.props.iconName) {
      console.error('Missing icon and iconName');
      return null;
    }
    const {
      icon,
      iconName,
      className,
      amp,
      children,
      ...otherProps
    } = this.props;
    let iconHtml = null;
    if (icon) {
      const picture: RequiredImage = {
        source: icon,
        width: 18,
        height: 18,
      };
      iconHtml = (
        <span className="fa fa-lg image-prefix-icon image-prefix-dancer">
          <AmpImage picture={picture} width="18" amp={this.props.amp} />
        </span>
      );
    } else if (this.props.iconName) {
      iconHtml = (
        <i className={`fa fa-${this.props.iconName} fa-lg image-prefix-icon`} />
      );
    }
    return (
      <span className={`image-prefix ${className || ''}`} {...otherProps}>
        {iconHtml}
        <span className="image-prefix-contents">
          {children}
        </span>
      </span>
    );
  }
}
