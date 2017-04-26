/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';

export default class FacebookShare extends React.Component {
  props: {
    url: string;
  }

  componentDidMount() {
    if (window.FB) {
      window.FB.XFBML.parse();
    }
  }

  render() {
    return <span style={{ verticalAlign: 'top' }} className="fb-share-button" data-href={this.props.url} data-layout="button" data-size="small" data-mobile-iframe="true" />;
  }
}
