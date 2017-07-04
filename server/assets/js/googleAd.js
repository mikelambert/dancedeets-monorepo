import React from 'react';

export default class GoogleAd extends React.Component {
  componentDidMount() {
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  }

  render() {
    // Google Ad: event-header
    return (
      <ins
        className="adsbygoogle"
        data-ad-client="ca-pub-9162736050652644"
        {...this.props}
      />
    );
  }
}
