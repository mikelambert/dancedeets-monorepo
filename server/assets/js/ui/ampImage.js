/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';

import type { Cover } from 'dancedeets-common/js/events/models';

export type RequiredImage = {
  source: number | string, // aka required package
  width: number,
  height: number,
};
type ClientCover = Cover | RequiredImage;

export class AmpImage extends React.Component {
  props: {
    picture: ClientCover,
    amp?: ?boolean,
    width?: string,
    srcSet?: string,
    sizes?: string,
  };

  render() {
    const { picture, amp, width, srcSet, sizes, ...otherProps } = this.props;
    if (this.props.amp) {
      return (
        <amp-img
          src={picture.source}
          layout="responsive"
          width={picture.width}
          height={picture.height}
          srcSet={srcSet}
          sizes={sizes}
        />
      );
    } else {
      return (
        <img
          role="presentation"
          src={picture.source}
          width={width}
          srcSet={srcSet}
          sizes={sizes}
          {...otherProps}
        />
      );
    }
  }
}
