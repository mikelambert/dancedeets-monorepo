/**
 * UI components stub for tutorials MVP
 * @flow
 */

import * as React from 'react';

// Type for window size props
export type windowProps = {
  width: number,
  height: number,
};

// Simple Link component
export function Link(props: {
  onClick?: () => void,
  href?: string,
  style?: Object,
  children?: React.Node,
}) {
  return (
    <a
      href={props.href || '#'}
      onClick={(e) => {
        if (props.onClick) {
          e.preventDefault();
          props.onClick();
        }
      }}
      style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer', ...props.style }}
    >
      {props.children}
    </a>
  );
}

// Simple Card component
export function Card(props: { style?: Object, children?: React.Node }) {
  return (
    <div
      style={{
        backgroundColor: 'white',
        borderRadius: 4,
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        overflow: 'hidden',
        ...props.style,
      }}
    >
      {props.children}
    </div>
  );
}

// Simple ShareLinks component
export function ShareLinks(props: { url: string }) {
  const encodedUrl = encodeURIComponent(props.url);
  return (
    <div style={{ display: 'flex', gap: 10, marginTop: 10 }}>
      <a
        href={`https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`}
        target="_blank"
        rel="noopener noreferrer"
        style={{ color: '#3b5998' }}
      >
        <i className="fa fa-facebook-square" aria-hidden="true" style={{ fontSize: 24 }} />
      </a>
      <a
        href={`https://twitter.com/intent/tweet?url=${encodedUrl}`}
        target="_blank"
        rel="noopener noreferrer"
        style={{ color: '#1da1f2' }}
      >
        <i className="fa fa-twitter" aria-hidden="true" style={{ fontSize: 24 }} />
      </a>
    </div>
  );
}

// HOC that provides window size props
export function wantsWindowSizes<Props: {}>(
  Component: React.ComponentType<{ ...Props, window: windowProps }>
): React.ComponentType<Props> {
  return class extends React.Component<Props, { window: windowProps }> {
    state = {
      window: {
        width: typeof window !== 'undefined' ? window.innerWidth : 1024,
        height: typeof window !== 'undefined' ? window.innerHeight : 768,
      },
    };

    componentDidMount() {
      window.addEventListener('resize', this.handleResize);
    }

    componentWillUnmount() {
      window.removeEventListener('resize', this.handleResize);
    }

    handleResize = () => {
      this.setState({
        window: {
          width: window.innerWidth,
          height: window.innerHeight,
        },
      });
    };

    render() {
      return <Component {...this.props} window={this.state.window} />;
    }
  };
}

// ImagePrefix component
export function ImagePrefix(props: { src: string, style?: Object }) {
  return <img src={props.src} style={props.style} alt="" />;
}

// AmpImage component (for AMP pages)
export function AmpImage(props: { src: string, width?: number, height?: number }) {
  return <img src={props.src} width={props.width} height={props.height} alt="" />;
}

export default { Link, Card, ShareLinks, wantsWindowSizes, ImagePrefix, AmpImage };
