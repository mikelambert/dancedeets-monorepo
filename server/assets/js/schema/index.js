/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';

export class JsonSchema extends React.Component {
  props: {
    json: ?Object,
  };

  render() {
    if (!this.props.json) {
      return null;
    }
    return (
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(this.props.json) }} // eslint-disable-line react/no-danger
      />
    );
  }
}
