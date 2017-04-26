/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  injectIntl,
  intlShape,
} from 'react-intl';

class _Message extends React.Component {
  props: {
    message: {
      /* eslint-disable react/no-unused-prop-types */
      // intlShape defines its formatMessage as func.isRequired,
      // but we know that it actually takes a few required parameters
      // which we include here to ensure our callers pass them in.
      id: string;
      defaultMessage: string;
      /* eslint-enable react/no-unused-prop-types */
    };
    values?: Object;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    return (<span>
      {this.props.intl.formatMessage(this.props.message, this.props.values)}
    </span>);
  }
}
export const Message = injectIntl(_Message);
