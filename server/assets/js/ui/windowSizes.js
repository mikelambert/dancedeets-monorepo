/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';

export type windowProps = {
  width: number,
  height: number,
};

export function wantsWindowSizes(WrappedComponent: Object) {
  class WindowSizes extends React.Component<
    {},
    {
      window: ?windowProps,
    }
  > {
    constructor(props: Object) {
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
        const width =
          window.innerWidth ||
          (document.documentElement && document.documentElement.clientWidth) ||
          (document.body && document.body.clientWidth);
        const height =
          window.innerHeight ||
          (document.documentElement && document.documentElement.clientHeight) ||
          (document.body && document.body.clientHeight);
        if (width != null && height != null) {
          return { window: { width, height } };
        }
      }
      return { window: null };
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
