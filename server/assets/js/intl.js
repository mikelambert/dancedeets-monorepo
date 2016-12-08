import React from 'react';
import {
  injectIntl,
  intlShape,
} from 'react-intl';

class _Message extends React.Component {
  props: {
    message: {
      id: string;
      defaultMessage: string;
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
