/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  View,
} from 'react-native';
import {
  injectIntl,
  defineMessages,
} from 'react-intl';
import { FeedListView } from '../learn/BlogList';
import {
  Card,
  Text,
} from '../ui';
import type {
  BattleCategory,
  Signup,
} from './models';
import {
  getCategorySignups,
} from './models';
import CategorySummaryCard from './categorySummaryCard';

class _TeamList extends React.Component {
  constructor(props: any) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderRow(signup: Signup) {
    const dancers = Object.keys(signup.dancers || {}).map(x =>
      <Text key={x} style={{ marginLeft: 20 }}>{signup.dancers ? signup.dancers[x].name : ''}</Text>
    );
    return (<Card>
      <Text>{signup.teamName}:</Text>
      {dancers}
    </Card>);
  }

  render() {
    return (<FeedListView
      items={this.props.signups}
      renderRow={this.renderRow}
      renderHeader={this.props.renderHeader}
    />);
  }
}
const TeamList = injectIntl(_TeamList);

class _BattleHostCategoryView extends React.Component {
  props: {
    category: BattleCategory;
  }

  render() {
    const signups = getCategorySignups(this.props.category);
    return (<TeamList
      signups={signups}
      renderHeader={() => <View
        style={{
          alignSelf: 'center',
          marginTop: 10,
        }}
      >
        <Text>{signups.length} competitors:</Text>
      </View>
      }
    />);
  }
}
const BattleHostCategoryView = injectIntl(_BattleHostCategoryView);

export default BattleHostCategoryView;
