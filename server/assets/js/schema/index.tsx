/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';

interface JsonSchemaProps {
  json: object | null;
}

export class JsonSchema extends React.Component<JsonSchemaProps> {
  render(): React.ReactNode {
    if (!this.props.json) {
      return null;
    }
    return (
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(this.props.json) }}
      />
    );
  }
}
