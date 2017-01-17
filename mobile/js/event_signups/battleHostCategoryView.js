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
import SwipeableListView from 'SwipeableListView';
import SwipeableQuickActions from 'SwipeableQuickActions';
import SwipeableQuickActionButton from 'SwipeableQuickActionButton';
import { FeedListView } from '../learn/BlogList';
import {
  Card,
  defaultFont,
  HorizontalView,
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
  props: {
    signups: Array<Signup>,
  };

  state: {
    dataSource: any;
  };

  constructor(props: any) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).renderQuickActions = this.renderQuickActions.bind(this);

    var ds = new SwipeableListView.getNewDataSource()
    // TODO: We need to "close off" signups and copy them to prelims at some point.
    // Then the numerical indices will be stable.
    this.state = {
      dataSource: ds.cloneWithRowsAndSections({s1: this.props.signups}, null, null)
    }
  }

  renderSignup(signup: Signup) {
    const dancers = Object.keys(signup.dancers || {}).map(x =>
      <Text key={x} style={{ marginLeft: 20 }}>{signup.dancers ? signup.dancers[x].name : ''}</Text>
    );
    return <View>
      <Text>Team: {signup.teamName}</Text>
      <HorizontalView>
        <Text>Dancers:</Text>
        <View>
          {dancers}
        </View>
      </HorizontalView>
    </View>;
  }

  renderRow(signup: Signup, sectionId: string, rowId: string) {
    const rowIndex = parseInt(rowId, 10) + 1;
    return (<Card>
      <HorizontalView>
        <Text style={{ marginRight: 10 }}>{rowIndex}:</Text>
        {this.renderSignup(signup)}
      </HorizontalView>
    </Card>);
  }

  renderQuickActions() {
    return <SwipeableQuickActions style={{
      alignItems: 'center',
      padding: 10,
    }}>
      <SwipeableQuickActionButton
        text="Called!"
        imageSource={require('../ui/FBButtons/images/facebook.png')}
        textStyle={defaultFont}
        onPress={() => console.log('1')}
      />
      <SwipeableQuickActionButton
        text="Danced!"
        imageSource={require('../ui/FBButtons/images/facebook.png')}
        textStyle={defaultFont}
        onPress={() => console.log('2')}
      />
    </SwipeableQuickActions>;
  }

  render() {
     return <SwipeableListView
      maxSwipeDistance={120}
      renderRow={this.renderRow}
      renderQuickActions={this.renderQuickActions}
      dataSource={this.state.dataSource}
      onScroll={(e) => {}}
    />;
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
