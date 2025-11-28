/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';

interface FacebookShareProps {
  url: string;
}

export default class FacebookShare extends React.Component<FacebookShareProps> {
  componentDidMount(): void {
    if (window.FB) {
      window.FB.XFBML.parse();
    }
  }

  render(): React.ReactNode {
    return (
      <span
        style={{ verticalAlign: 'top' }}
        className="fb-share-button"
        data-href={this.props.url}
        data-layout="button"
        data-size="small"
        data-mobile-iframe="true"
      />
    );
  }
}
