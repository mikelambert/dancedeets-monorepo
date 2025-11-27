/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';

export interface WindowProps {
  width: number;
  height: number;
}

interface WindowSizesState {
  window: WindowProps | null;
}

export function wantsWindowSizes<P extends object>(
  WrappedComponent: React.ComponentType<P & { window?: WindowProps | null }>
): React.ComponentType<Omit<P, 'window'>> {
  class WindowSizes extends React.Component<Omit<P, 'window'>, WindowSizesState> {
    constructor(props: Omit<P, 'window'>) {
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

      this.updateDimensions = this.updateDimensions.bind(this);
    }

    componentDidMount(): void {
      window.addEventListener('resize', this.updateDimensions);
    }

    componentWillUnmount(): void {
      window.removeEventListener('resize', this.updateDimensions);
    }

    getWindowState(): WindowSizesState {
      if (typeof window !== 'undefined') {
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

    updateDimensions(): void {
      this.setState(this.getWindowState());
    }

    render(): React.ReactNode {
      return (
        <WrappedComponent
          {...(this.props as P)}
          window={this.state.window}
        />
      );
    }
  }
  return WindowSizes;
}
