/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { Share as TwitterShare } from 'react-twitter-widgets';
import FacebookShare from './fbShare';

export default class ShareLinks extends React.Component {
  props: {
    url: string,
  };

  render() {
    return (
      <div>
        <span style={{ display: 'inline-block' }}>
          <TwitterShare url={this.props.url} />
        </span>
        <span className="link-event-share">
          <FacebookShare url={this.props.url} />
        </span>
      </div>
    );
  }
}
