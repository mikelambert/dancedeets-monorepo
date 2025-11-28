/**
 * Copyright 2016 DanceDeets.
 */

import { defineMessages } from 'react-intl';

export const messages = defineMessages({
  nearbyPromoters: {
    id: 'peopleList.nearbyPromoters',
    defaultMessage: 'Nearby Promoters',
    description: 'Title for pop-open list of promoters/organizers in the scene',
  },
  nearbyPromotersMessage: {
    id: 'peopleList.nearbyPromotersMessage',
    defaultMessage: 'If you want to organize an event, work with these folks',
    description:
      'Subtitle for pop-open list of promoters/organizers in the scene',
  },
  nearbyDancers: {
    id: 'peopleList.nearbyDancers',
    defaultMessage: 'Nearby Dancers',
    description: 'Title for pop-open list of dancers in the scene',
  },
  nearbyDancersMessage: {
    id: 'peopleList.nearbyDancersMessage',
    defaultMessage: 'These people are active in the local dance scene',
    description: 'Subtitle for pop-open list of dancers in the scene',
  },
  nooneNearby: {
    id: 'peopleList.nooneNearby',
    defaultMessage: 'No one found nearby.',
    description:
      'Error message shown when there are no people to recommend in this area',
  },
});
