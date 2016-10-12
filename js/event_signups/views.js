/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import {
  AlertIOS,
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
  semiNormalize,
  normalize,
} from '../ui/normalize';
import { connect } from 'react-redux';
import type { Dispatch } from '../actions/types';
import {
  setTutorialVideoIndex,
} from '../actions';
import { googleKey } from '../keys';


class _EventSignups extends React.Component {
  constructor(props: any) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderRow(category: any) {
    return <TouchableHighlight
      onPress={() => {
        this.props.onSelected(category);
      }}
      >
      <View
        style={{
          backgroundColor: purpleColors[2],
        }}>
        <Text style={[]}>{category}</Text>
      </View>
    </TouchableHighlight>;
  }

  render() {
    return <FeedListView
      items={this.props.categories}
      renderRow={this.renderRow}
      />;
  }
}
const EventSignups = injectIntl(_EventSignups);

class _SignupList extends React.Component {
  constructor(props: any) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderRow(signup: any) {
    return <Text>{signup}</Text>;
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
      <Text>{this.props.category}</Text>
      <Button>Signup</Button>
      <SignupList signups={[
        'a',
        'b',
        'c',
      ]}/>
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
          this.props.navigatable.onNavigate({key: 'Category', title: category.name, category: category});
        }}
        categories={
          [
          'BBoy 1x1',
          'House 2x2',
          ]
        }
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
