/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import Measure, { ContentRect } from 'react-measure';

interface TruncateProps {
  height: number;
  children: React.ReactNode;
}

interface TruncateState {
  expanded: boolean;
  loading: boolean;
  needsToggle: boolean;
}

export default class Truncate extends React.Component<TruncateProps, TruncateState> {
  constructor(props: TruncateProps) {
    super(props);
    this.state = { expanded: false, loading: true, needsToggle: true };
    this.toggleVisibility = this.toggleVisibility.bind(this);
    this.onResize = this.onResize.bind(this);
  }

  onResize(contentRect: ContentRect): void {
    this.setState({
      loading: false,
    });
    if (
      contentRect.scroll &&
      contentRect.bounds &&
      contentRect.scroll.height <= contentRect.bounds.height
    ) {
      this.setState({ needsToggle: false });
    }
  }

  toggleVisibility(): void {
    this.setState({ expanded: !this.state.expanded });
  }

  render(): React.ReactNode {
    if (!this.state.needsToggle || this.state.expanded) {
      return (
        <div>
          <div>{this.props.children}</div>
          {this.state.needsToggle ? (
            <button className="link-button" onClick={this.toggleVisibility}>
              Show less...
            </button>
          ) : null}
        </div>
      );
    } else {
      let loadMoreButton: React.ReactNode = null;
      if (!this.state.loading) {
        loadMoreButton = (
          <button className="link-button" onClick={this.toggleVisibility}>
            Show more...
          </button>
        );
      }
      return (
        <div style={{ height: this.props.height }}>
          <Measure scroll bounds onResize={this.onResize}>
            {({ measureRef }) => (
              <div
                ref={measureRef}
                className="fade-out-body"
                style={{
                  overflow: 'hidden',
                  height: '100%',
                }}
              >
                {this.props.children}
              </div>
            )}
          </Measure>
          {loadMoreButton}
        </div>
      );
    }
  }
}
