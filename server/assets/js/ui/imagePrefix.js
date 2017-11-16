/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import classNames from 'classnames';
import { AmpImage } from './ampImage';
import type { RegularImage, ImportedImage } from './ampImage';

export class ImagePrefix extends React.Component<{
  icon?: number, // aka required package
  iconUrl?: string,
  iconName?: string,
  className?: string,
  amp?: boolean,
  children: React.Node,
}> {
  render() {
    if (!this.props.icon && !this.props.iconName && !this.props.iconUrl) {
      console.error('Missing icon and iconName and iconUrl');
      return null;
    }
    const {
      icon,
      iconUrl,
      iconName,
      className,
      amp,
      children,
      ...otherProps
    } = this.props;
    let iconHtml = null;
    if (icon) {
      const picture: ImportedImage = {
        uri: icon,
        width: 18,
        height: 18,
      };
      iconHtml = (
        <span className="fa fa-lg image-prefix-icon image-prefix-dancer">
          <AmpImage picture={picture} width="18" amp={this.props.amp} />
        </span>
      );
    } else if (iconUrl) {
      const picture: RegularImage = {
        uri: iconUrl,
        width: 18,
        height: 18,
      };
      iconHtml = (
        <span className="fa fa-lg image-prefix-icon image-prefix-dancer">
          <AmpImage picture={picture} width="18" amp={this.props.amp} />
        </span>
      );
    } else if (iconName) {
      iconHtml = <i className={`fa fa-${iconName} fa-lg image-prefix-icon`} />;
    }
    return (
      <div className={`image-prefix ${className || ''}`} {...otherProps}>
        {iconHtml}
        <span className="image-prefix-contents">{children}</span>
      </div>
    );
  }
}

export class ImagePrefixInline extends React.Component<{
  className?: string,
  children: React.Node,
}> {
  render() {
    const { className, ...otherProps } = this.props;
    return (
      <ImagePrefix className={classNames(className, 'span')} {...otherProps} />
    );
  }
}
