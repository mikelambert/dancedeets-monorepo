/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { Dimensions, FlatList, TouchableHighlight, View } from 'react-native';
import { injectIntl, defineMessages } from 'react-intl';
import FitImage from 'react-native-fit-image';
import type { Dispatch, User } from '../actions/types';
import type { BattleCategory, BattleEvent, Signup } from './models';
import CategorySummaryCard from './categorySummaryCard';

const boxMargin = 5;

class _BattleEventView extends React.Component {
  props: {
    battleId: string,
    battleEvent: BattleEvent,
    onSelected: (category: BattleCategory) => void,
    onRegister: (category: BattleCategory) => void,
    onUnregister: (category: BattleCategory, team: Signup) => void,
  };

  constructor(props: any) {
    super(props);
    (this: any).renderHeader = this.renderHeader.bind(this);
    (this: any).renderRow = this.renderRow.bind(this);
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

  renderRow(row) {
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
          data={this.props.battleEvent.categories}
          renderHeader={this.renderHeader}
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
const BattleEventView = injectIntl(_BattleEventView);

export default BattleEventView;
