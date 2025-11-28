/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import LazyLoad from 'react-lazyload';
import { SearchEvent } from 'dancedeets-common/js/events/models';

interface SquareEventFlyerProps {
  event: SearchEvent;
  lazyLoad?: boolean;
}

export class SquareEventFlyer extends React.Component<SquareEventFlyerProps> {
  render(): React.ReactNode {
    const { event } = this.props;
    const width = 180;
    const height = 180;

    const croppedPicture = this.props.event.getCroppedCover(width, height);
    if (!croppedPicture) {
      return null;
    }
    let imageTag: React.ReactNode = (
      <div className="square-flyer">
        <img alt="" src={croppedPicture.uri} className="full-width no-border" />
      </div>
    );
    if (this.props.lazyLoad) {
      imageTag = (
        <LazyLoad height={height} once offset={300}>
          {imageTag}
        </LazyLoad>
      );
    }
    return (
      <a className="link-event-flyer" href={event.getUrl()}>
        {imageTag}
      </a>
    );
  }
}
