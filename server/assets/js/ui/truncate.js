/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import Measure from 'react-measure';

type Rect = {
  top: number,
  left: number,
  width: number,
  height: number,
};

type Props = {
  height: number,
  children: React.Element<*>,
};

export default class Truncate extends React.Component {
  props: Props;

  state: {
    expanded: boolean,
    loading: boolean,
    needsToggle: boolean,
  };

  _div: React.Element<*>;

  constructor(props: Props) {
    super(props);
    this.state = { expanded: false, loading: true, needsToggle: true };
    (this: any).toggleVisibility = this.toggleVisibility.bind(this);
    (this: any).onResize = this.onResize.bind(this);
  }

  onResize(contentRect: { scroll: Rect, bounds: Rect }) {
    this.setState({
      loading: false,
    });
    if (contentRect.scroll.height <= contentRect.bounds.height) {
      this.setState({ needsToggle: false });
    }
  }

  toggleVisibility() {
    this.setState({ expanded: !this.state.expanded });
  }

  render() {
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
      let loadMoreButton = null;
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
