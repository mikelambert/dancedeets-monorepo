/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import {
  Dimensions,
  FlatList,
  Text,
  TouchableHighlight,
  View,
} from 'react-native';
import FitImage from 'react-native-fit-image';
import type { BattleCategory, BattleEvent } from './models';
import { getCategories } from './models';
import { Button } from '../ui';

const boxMargin = 5;

interface BattleEventHostViewProps {
  battleId?: string;
  battleEvent: BattleEvent;
  onSelected: (category: BattleCategory) => void;
}

class _BattleEventHostView extends React.Component<BattleEventHostViewProps> {
  constructor(props: BattleEventHostViewProps) {
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
export default _BattleEventHostView;
