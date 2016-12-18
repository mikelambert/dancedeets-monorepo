/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  intlWeb,
} from 'dancedeets-common/js/intl';

class Tutorial extends React.Component {
  render() {
    return <div>AA {this.props.toString()}</div>;
  }
}

export default intlWeb(Tutorial);
