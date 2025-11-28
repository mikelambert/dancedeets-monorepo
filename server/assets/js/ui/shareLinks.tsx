/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { Share as TwitterShare } from 'react-twitter-widgets';
import FacebookShare from './fbShare';

interface ShareLinksProps {
  url: string;
}

export default class ShareLinks extends React.Component<ShareLinksProps> {
  render(): React.ReactNode {
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
