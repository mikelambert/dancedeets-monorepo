/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { injectIntl, WrappedComponentProps, MessageDescriptor } from 'react-intl';

interface MessageProps {
  message: MessageDescriptor;
  values?: Record<string, string | number>;
}

class _Message extends React.Component<MessageProps & WrappedComponentProps> {
  render(): React.ReactNode {
    return (
      <span>
        {this.props.intl.formatMessage(this.props.message, this.props.values)}
      </span>
    );
  }
}

export const Message = injectIntl(_Message);
