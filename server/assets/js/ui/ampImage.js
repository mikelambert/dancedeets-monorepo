/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import type {
  ImageWithSizes,
  ImageOptionalSizes,
} from 'dancedeets-common/js/events/models';

export type ImportedImage = {
  uri: number, // aka require()'d package
  width: ?number,
  height: ?number,
};
type ClientImage = ImportedImage | ImageOptionalSizes | ImageWithSizes;

export class AmpImage extends React.Component<{
  picture: ClientImage,
  amp?: ?boolean,
  width?: string,
  srcSet?: string,
  sizes?: string,
}> {
  render() {
    const { picture, amp, width, srcSet, sizes, ...otherProps } = this.props;
    if (this.props.amp) {
      return (
        <amp-img
          src={picture.uri}
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
          alt="" // Possibly overridden in caller's props
          src={picture.uri}
          width={width}
          srcSet={srcSet}
          sizes={sizes}
          {...otherProps}
        />
      );
    }
  }
}
