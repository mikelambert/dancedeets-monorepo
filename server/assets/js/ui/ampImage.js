/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';

import type {
  Cover,
} from 'dancedeets-common/js/events/models';

export type RequiredImage = {
  source: number; // aka required package
  width: number;
  height: number;
};
type ClientCover = Cover | RequiredImage;

export class AmpImage extends React.Component {
  props: {
    picture: ClientCover;
    amp?: ?boolean;
    width?: string;
  }

  render() {
    const { picture, amp, width, ...otherProps } = this.props;
    if (this.props.amp) {
      return (
        <amp-img
          src={picture.source}
          layout="responsive"
          width={picture.width}
          height={picture.height}
        />
      );
    } else {
      return (
        <img
          role="presentation"
          src={picture.source}
          width={width}
          {...otherProps}
        />
      );
    }
  }
}
