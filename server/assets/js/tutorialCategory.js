/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  intlWeb,
} from 'dancedeets-common/js/intl';
import {
  getTutorials,
} from 'dancedeets-common/js/tutorials/playlistConfig';
import {
  injectIntl,
  intlShape,
} from 'react-intl';

class _TutorialCategory extends React.Component {
  props: {
    style: string;

    // Self-managed props
    intl: intlShape;
  }

  state: {
    tutorials: Array<{
      style: Object,
      tutorials: Array<Object>,
    }>;
  }

  constructor(props) {
    super(props);
    this.state = {
      tutorials: getTutorials(this.props.intl.locale),
    };
  }

  render() {
    const matching = this.state.tutorials.filter(category => category.style.id === this.props.style);

    if (matching) {
      const category = matching[0];

      return <div>{category.style.title}</div>;
    }
    return <div>Nope</div>;
  }
}
const TutorialCategory = injectIntl(_TutorialCategory);

export default intlWeb(TutorialCategory);
