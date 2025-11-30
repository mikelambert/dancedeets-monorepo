/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { Dimensions, FlatList, TouchableHighlight, View } from 'react-native';
import FitImage from 'react-native-fit-image';
import type { BattleCategory, BattleEvent, Signup } from './models';
import { getCategories } from './models';
import CategorySummaryCard from './categorySummaryCard';

const boxMargin = 5;

interface BattleEventViewProps {
  battleId?: string;
  battleEvent: BattleEvent;
  onSelected: (category: BattleCategory) => void;
  onRegister: (category: BattleCategory) => void;
  onUnregister: (category: BattleCategory, team: Signup) => void;
}

class _BattleEventView extends React.Component<BattleEventViewProps> {
  constructor(props: BattleEventViewProps) {
    super(props);
    this.renderHeader = this.renderHeader.bind(this);
    this.renderRow = this.renderRow.bind(this);
  }

  renderHeader() {
    return (
      <FitImage
        source={{ uri: this.props.battleEvent.headerImageUrl }}
        // TODO: set this height dynamically, perhaps from the json data
        style={{ flex: 1, width: Dimensions.get('window').width, height: 200 }}
      />
    );
  }

  renderRow(row: { item: BattleCategory }) {
    const category = row.item;
    return (
      <TouchableHighlight
        onPress={() => {
          this.props.onSelected(category);
        }}
        style={{
          margin: boxMargin,
          borderRadius: 10,
        }}
      >
        <CategorySummaryCard
          category={category}
          onRegister={this.props.onRegister}
          onUnregister={this.props.onUnregister}
        />
      </TouchableHighlight>
    );
  }

  render() {
    let view = null;
    if (this.props.battleEvent) {
      view = (
        <FlatList
          data={getCategories(this.props.battleEvent)}
          ListHeaderComponent={this.renderHeader}
          renderItem={this.renderRow}
          contentContainerStyle={{
            alignSelf: 'center',
            justifyContent: 'flex-start',
            alignItems: 'center',
          }}
        />
      );
    }
    return view;
  }
}
export default _BattleEventView;
