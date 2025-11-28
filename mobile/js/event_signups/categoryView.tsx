/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { FlatList, View } from 'react-native';
import { injectIntl, defineMessages } from 'react-intl';
import { Card, Text } from '../ui';
import type { BattleCategory, Signup } from './models';
import { getCategorySignups } from './models';
import CategorySummaryCard from './categorySummaryCard';

interface TeamListProps {
  signups: Array<Signup>;
  renderHeader?: () => React.ReactElement;
}

class _TeamList extends React.Component<TeamListProps> {
  constructor(props: TeamListProps) {
    super(props);
    this.renderRow = this.renderRow.bind(this);
  }

  renderRow(row: { item: Signup }) {
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

interface CategoryViewProps {
  category: BattleCategory;
  onRegister: (category: BattleCategory) => void;
  onUnregister: (category: BattleCategory, team: Signup) => void;
}

class _CategoryView extends React.Component<CategoryViewProps> {
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
