/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import {
  Dimensions,
  FlatList,
  Text,
  TouchableHighlight,
  View,
} from 'react-native';
import { injectIntl, defineMessages } from 'react-intl';
import FitImage from 'react-native-fit-image';
import type { Dispatch, User } from '../actions/types';
import type { BattleCategory, BattleEvent, Signup } from './models';
import { getCategories } from './models';
import { Button } from '../ui';
import CategorySummaryCard from './categorySummaryCard';

const boxMargin = 5;

class _BattleEventHostView extends React.Component<{
  battleId: string,
  battleEvent: BattleEvent,
  onSelected: (category: BattleCategory) => void,
}> {
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
      <Button
        onPress={() => {
          this.props.onSelected(category);
        }}
        style={{
          margin: boxMargin,
          borderRadius: 10,
        }}
        caption={category.display.name}
      />
    );
  }

  render() {
    let view = null;
    if (this.props.battleEvent) {
      view = (
        <FlatList
          data={getCategories(this.props.battleEvent)}
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
const BattleEventHostView = injectIntl(_BattleEventHostView);

export default BattleEventHostView;
