/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import type {
  Cover,
} from 'dancedeets-common/js/events/models';

type RequiredImage = {
  source: number; // aka required package
  width: number;
  height: number;
};
type ClientCover = Cover | RequiredImage;

export class Card extends React.Component {
  props: {
    children?: Array<React.Element<*>>;
    className?: string;
  }

  render() {
    const { children, className, ...otherProps } = this.props;
    return (<div className={`card ${className || ''}`} {...otherProps} >
      {children}
    </div>);
  }
}

export class ImagePrefix extends React.Component {
  props: {
    icon?: number; // aka required package
    iconName?: string;
    className?: string;
    amp?: boolean;
    children?: Array<React.Element<*>>;
  }

  render() {
    if (!this.props.icon && !this.props.iconName) {
      console.error('Missing icon and iconName');
      return null;
    }
    const { icon, iconName, className, amp, children, ...otherProps } = this.props;
    let iconHtml = null;
    if (icon) {
      const picture: RequiredImage = {
        source: icon,
        width: 18,
        height: 18,
      };
      iconHtml = (<span className="fa fa-lg image-prefix-icon image-prefix-dancer">
        <AmpImage
          picture={picture}
          width="18"
          amp={this.props.amp}
        />
      </span>);
    } else if (this.props.iconName) {
      iconHtml = <i className={`fa fa-${this.props.iconName} fa-lg image-prefix-icon`} />;
    }
    return (<div className={`image-prefix ${className || ''}`} {...otherProps}>
      {iconHtml}
      <div className="image-prefix-contents">
        {children}
      </div>
    </div>);
  }
}

export class AmpImage extends React.Component {
  props: {
    picture: ClientCover;
    amp?: boolean;
    width?: string;
  }

  render() {
    const { picture, amp, width, ...otherProps } = this.props;
    if (this.props.amp) {
      return (
        <amp-img
          src={picture.source}
          layout="responsive"
          width={picture.width}
          height={picture.height}
        />
      );
    } else {
      return (
        <img
          role="presentation"
          src={picture.source}
          width={width}
          {...otherProps}
        />
      );
    }
  }
}

export class Link extends React.Component {
  props: {
    children?: any;
    style?: any;
  }
  render() {
    const { children, style, ...otherProps } = this.props;
    const fullStyle = { cursor: 'pointer', ...style };
    return <div style={fullStyle} {...otherProps}>{children}</div>;
  }
}

export function wantsWindowSizes(WrappedComponent: Object) {
  class WindowSizes extends React.Component {
    state: {
      window: ?{
        width: number;
        height: number;
      };
    }

    constructor(props) {
      super(props);

      // Unfortunately, sticking this code into the constructor directly,
      // triggers a different initial render() than on the server,
      // which triggers invalid checksums and a full react clientside re-render.
      //
      // I can try to avoid it, by doing it on a subsequent render,
      // but I have the same problem with the selected-videoIndex,
      // which triggers a different row highlight than was presupposed by the server.
      //
      // But I'd prefer to have a fast-loading initial page, so instead,
      // I give up and just accept these dev-mode-only warnings:
      // 'React attempted to reuse markup in a container but the checksum was invalid.''

      this.state = {
        ...this.getWindowState(),
      };

      (this: any).updateDimensions = this.updateDimensions.bind(this);
    }

    componentDidMount() {
      window.addEventListener('resize', this.updateDimensions);
    }

    componentWillUnmount() {
      window.removeEventListener('resize', this.updateDimensions);
    }

    getWindowState() {
      if (global.window != null) {
        const width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
        const height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
        return { window: { width, height } };
      } else {
        return { window: null };
      }
    }

    updateDimensions() {
      this.setState(this.getWindowState());
    }

    render() {
      return <WrappedComponent {...this.props} window={this.state.window} />;
    }
  }
  return WindowSizes;
}

export type windowProps = {
  width: number,
  height: number,
};
