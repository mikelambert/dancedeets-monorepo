/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';

export default class GoogleAd extends React.Component {
  props: {
    style: Object,
    amp?: boolean,
  };

  componentDidMount() {
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  }

  render() {
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
