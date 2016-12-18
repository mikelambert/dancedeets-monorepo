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
  getTutorials
} from 'dancedeets-common/js/tutorials/playlistConfig';

class TutorialCategory extends React.Component {
  props: {
    style: string;
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
      tutorials: getTutorials(),
    };
  }

  render() {
    const matching = this.state.tutorials.filter(category => category.style.id == this.props.style);

    if (matching) {
      const category = matching[0];

      return <div>{category.style.title}</div>;
    }
    return <div>Nope</div>;
  }
}

export default intlWeb(TutorialCategory);
