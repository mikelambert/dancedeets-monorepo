/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { FlatList, View } from 'react-native';
import { injectIntl, defineMessages } from 'react-intl';
import { Card, Text } from '../ui';
import type { BattleCategory, Signup } from './models';
import { getCategorySignups } from './models';
import CategorySummaryCard from './categorySummaryCard';

class _TeamList extends React.Component {
  constructor(props: any) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
  }

  renderRow(row) {
    const signup = row.item;
    const dancers = (signup.dancers || []).map(x => (
      <Text key={x.id} style={{ marginLeft: 20 }}>
        {x.name}
      </Text>
    ));
    return (
      <Card>
        <Text>{signup.teamName}:</Text>
        {dancers}
      </Card>
    );
  }

  render() {
    return (
      <FlatList
        data={this.props.signups}
        renderItem={this.renderRow}
        renderHeader={this.props.renderHeader}
      />
    );
  }
}
const TeamList = injectIntl(_TeamList);

class _CategoryView extends React.Component {
  props: {
    category: BattleCategory,
    onRegister: (category: BattleCategory) => void,
    onUnregister: (category: BattleCategory, team: Signup) => void,
  };

  render() {
    const signups = getCategorySignups(this.props.category);
    return (
      <TeamList
        signups={signups}
        renderHeader={() => (
          <View
            style={{
              alignSelf: 'center',
              marginTop: 10,
            }}
          >
            <CategorySummaryCard
              category={this.props.category}
              onRegister={this.props.onRegister}
              onUnregister={this.props.onUnregister}
            />
            <Text>{signups.length} competitors:</Text>
          </View>
        )}
      />
    );
  }
}
const CategoryView = injectIntl(_CategoryView);

export default CategoryView;
