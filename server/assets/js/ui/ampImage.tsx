/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import type {
  ImageWithSizes,
  ImageOptionalSizes,
} from 'dancedeets-common/js/events/models';

export interface ImportedImage {
  uri: number; // aka require()'d package
  width?: number | null;
  height?: number | null;
}

type ClientImage = ImportedImage | ImageOptionalSizes | ImageWithSizes;

export interface AmpImageProps {
  picture: ClientImage;
  amp?: boolean | null;
  width?: string;
  srcSet?: string;
  sizes?: string;
  alt?: string;
  className?: string;
  style?: React.CSSProperties;
}

export class AmpImage extends React.Component<AmpImageProps> {
  render(): React.ReactNode {
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
          src={picture.uri as string}
          width={width}
          srcSet={srcSet}
          sizes={sizes}
          {...otherProps}
        />
      );
    }
  }
}
