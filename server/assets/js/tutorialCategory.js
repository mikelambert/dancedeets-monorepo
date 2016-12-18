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
  defaultTutorials
} from 'dancedeets-common/js/tutorials/playlistConfig';

class TutorialCategory extends React.Component {
  props: {
    style: string;
  }

  render() {
    const matching = defaultTutorials.filter(category => category.style.id == this.props.style);

    if (matching) {
      const category = matching[0];

      return <div><img src={category.style.} /></div>;
    }
    return <div>Nope</div>;
  }
}

export default intlWeb(TutorialCategory);
