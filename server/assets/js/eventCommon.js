/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import LazyLoad from 'react-lazyload';
import { SearchEvent } from 'dancedeets-common/js/events/models';

export class SquareEventFlyer extends React.Component<{
  event: SearchEvent,
  lazyLoad?: boolean,
}> {
  render() {
    const event = this.props.event;
    const width = 180;
    const height = 180;

    const croppedPicture = this.props.event.getCroppedCover(width, height);
    if (!croppedPicture) {
      return null;
    }
    let imageTag = (
      <div className="square-flyer">
        <img
          role="presentation"
          src={croppedPicture.source}
          className="full-width no-border"
        />
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
