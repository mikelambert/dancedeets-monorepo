/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';

interface GoogleAdProps {
  style: React.CSSProperties & { width: number | string; height: number | string };
  amp?: boolean | null;
  'data-ad-slot'?: string;
}

export default class GoogleAd extends React.Component<GoogleAdProps> {
  componentDidMount(): void {
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  }

  render(): React.ReactNode {
    const { amp, ...props } = this.props;
    if (this.props.amp) {
      const { style, ...otherProps } = props;
      return (
        <div>
          <amp-ad
            layout="responsive"
            width={this.props.style.width}
            height={this.props.style.height}
            type="adsense"
            data-ad-client="ca-pub-9162736050652644"
            {...otherProps}
          />
        </div>
      );
    } else {
      return (
        <ins
          className="adsbygoogle"
          data-ad-client="ca-pub-9162736050652644"
          {...props}
        />
      );
    }
  }
}
