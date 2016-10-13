/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  AlertIOS,
  Animated,
  Dimensions,
  Image,
  ListView,
  StyleSheet,
  TouchableHighlight,
  View,
} from 'react-native';
import _ from 'lodash/string';
import { track } from '../store/track';
import YouTube from 'react-native-youtube';
import { FeedListView } from '../learn/BlogList';
import {
  Button,
  HorizontalView,
  Text,
} from '../ui';
import { purpleColors } from '../Colors';
import shallowEqual from 'fbjs/lib/shallowEqual';
import styleEqual from 'style-equal';
import {
  injectIntl,
  defineMessages,
} from 'react-intl';
import languages from '../languages';
import {
  Card,
  semiNormalize,
  normalize,
  ProportionalImage,
} from '../ui';
import { connect } from 'react-redux';
import type { Dispatch } from '../actions/types';
import {
  setTutorialVideoIndex,
} from '../actions';
import { googleKey } from '../keys';
import {
  CompetitionCategory,
} from './models';
import type {
  Signup,
} from './models';
import danceStyles from '../styles';

// Trying to emulate Just Debout
const categories: Array<CompetitionCategory> = [
  new CompetitionCategory({
    name: 'Hip-Hop',
    styleIcon: 'hiphop',
    teamSize: 2,
    signups: [
      {
        teamName: 'Step Funktion',
        dancers: [
          {
            uid: '701004',
            name: 'Mike Lambert'
          },
        ],
      },
    ],
  }),
  new CompetitionCategory({
    name: 'House',
    styleIcon: 'house',
    teamSize: 2,
    signups: [
      {
        teamName: 'Apartment Feet',
        dancers: [
          {
            uid: '701004',
            name: 'Mike Lambert'
          },
        ],
      },
    ],
  }),
  new CompetitionCategory({
    name: 'Popping',
    styleIcon: 'pop',
    teamSize: 2,
    signups: [
      {
        teamName: 'Stack Poppers',
        dancers: [
          {
            uid: '701004',
            name: 'Mike Lambert'
          },
        ],
      },
    ],
  }),
  new CompetitionCategory({
    name: 'Locking',
    styleIcon: 'lock',
    teamSize: 2,
    signups: [
      {
        teamName: 'Lock Racing',
        dancers: [
          {
            uid: '701004',
            name: 'Mike Lambert'
          },
        ],
      },
    ],
  }),
  new CompetitionCategory({
    name: 'Top Rock',
    styleIcon: 'break',
    teamSize: 1,
    signups: [
      {
        teamName: 'Upper Pebbles',
        dancers: [
          {
            uid: '701004',
            name: 'Mike Lambert'
          },
        ],
      },
    ],
  }),
];


// Try to make our boxes as wide as we can...
let boxWidth = normalize(350);
// ...and only start scaling them non-proportionally on the larger screen sizes,
// so that we do 3-4 columns
if (Dimensions.get('window').width >= 1024) {
  boxWidth = semiNormalize(350);
}
const boxMargin = 5;

class _EventSignups extends React.Component {
  constructor(props: any) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  dancerIcons(category: any) {
    const teamSize = Math.max(category.teamSize, 1);

    const images = [];
    const margin = 30;
    const imageWidth = (boxWidth - 30 - margin) / (2 * Math.max(teamSize, 2));
    for (let i = 0; i < teamSize; i++) {
      images.push(<ProportionalImage
        resizeDirection="width"
        source={danceStyles[category.styleIcon].thumbnail}
        originalWidth={danceStyles[category.styleIcon].width}
        originalHeight={danceStyles[category.styleIcon].height}
        resizeMode="contain"
        style={{
          height: imageWidth,
        }}
      />);
    }
    return <HorizontalView>{images}</HorizontalView>;
  }

  renderRow(category: any) {
    const dancerIcons = this.dancerIcons(category);
    return <TouchableHighlight
      onPress={() => {
        this.props.onSelected(category);
      }}
      style={{
        margin: boxMargin,
        borderRadius: 10,
      }}
      >
      <View
        style={{
          width: boxWidth,
          backgroundColor: purpleColors[2],
          padding: 5,
          borderRadius: 10,
        }}>
        <HorizontalView style={{justifyContent: 'space-between'}}>
          <View>{dancerIcons}</View>
          <Animated.View style={{position:'relative',transform:[{skewY: '-180deg'}]}}>{dancerIcons}</Animated.View>
        </HorizontalView>
        <Text style={{marginVertical: 10, textAlign: 'center', fontWeight: 'bold', fontSize: semiNormalize(30), lineHeight: semiNormalize(34)}}>{category.displayName()}</Text>
      </View>
    </TouchableHighlight>;
  }

  render() {
    return <FeedListView
      items={this.props.categories}
      renderRow={this.renderRow}
      contentContainerStyle={{
        alignSelf: 'center',
        justifyContent: 'flex-start',
        flexDirection: 'row',
        flexWrap: 'wrap',
        alignItems: 'flex-start',
      }}
      />;
  }
}
const EventSignups = injectIntl(_EventSignups);

class _SignupList extends React.Component {
  constructor(props: any) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderRow(signup: Signup) {
    const dancers = signup.dancers.map((x) => <Text key={x.uid}>{x.name}</Text>);
    return <Card>
      <Text>{signup.teamName}</Text>
      {dancers}
    </Card>;
  }

  render() {
    return <FeedListView
      items={this.props.signups}
      renderRow={this.renderRow}
      />;
  }
}
const SignupList = injectIntl(_SignupList);

class _Category extends React.Component {
  constructor(props: any) {
    super(props);
  }

  render() {
    return <View>
      <Button caption="Sign Up" style={{width: semiNormalize(200), height: semiNormalize(50)}}/>
      <Text>{this.props.category.signups.length} competitors:</Text>
      <SignupList signups={this.props.category.signups} />
    </View>;
  }
}
const Category = injectIntl(_Category);

class _EventSignupsView extends React.Component {
  render() {
    const { scene } = this.props.sceneProps;
    const { route } = scene;
    switch (route.key) {
    case 'EventSignups':
      return <EventSignups
        onSelected={(category) => {
          //trackWithEvent('View Event', event);
          this.props.navigatable.onNavigate({key: 'Category', title: category.displayName(), category: category});
        }}
        categories={categories}
      />;
    case 'Category':
      return <Category
        category={route.category}
        />;
    }
  }
}
export const EventSignupsView = injectIntl(_EventSignupsView);


let styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  miniThumbnail: {
    height: 50,
    flex: 1,
  },
});
