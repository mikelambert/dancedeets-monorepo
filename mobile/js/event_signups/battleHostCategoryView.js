/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  ListView,
  TouchableOpacity,
  View,
} from 'react-native';
import {
  injectIntl,
  defineMessages,
} from 'react-intl';
import { FeedListView } from '../learn/BlogList';
import {
  Card,
  defaultFont,
  HorizontalView,
  RibbonBanner,
  Text,
} from '../ui';
import type {
  BattleCategory,
  PrelimStatus,
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
    prelims: Array<PrelimStatus>;
    dataSource: ListView.DataSource;
  };

  constructor(props: any) {
    super(props);
    (this: any).renderRow = this.renderRow.bind(this);
    (this: any).onSignupPressed = this.onSignupPressed.bind(this);

    // TODO: We need to "close off" signups and copy them to prelims at some point.
    // Then the numerical indices will be stable.
    const prelims = this.props.signups.map(signup => ({
      signupKey: signup.id,
      auditioned: false,
    }));
    this.state = this.prelimsState(prelims);
  }

  prelimsState(prelims) {
    const ds = (this.state && this.state.dataSource) || new ListView.DataSource({
      rowHasChanged: (r1, r2) => r1 !== r2,
    });
    return {
      prelims,
      dataSource: ds.cloneWithRows(prelims, null, null),
    };
  }

  renderSignup(signup: Signup) {
    const dancers = Object.keys(signup.dancers || {}).map(x =>
      <Text key={x}>{signup.dancers ? signup.dancers[x].name : ''}</Text>
    );
    return <View>
      <HorizontalView>
        <Text>Team: </Text>
        <Text>{signup.teamName}</Text>
      </HorizontalView>
      <HorizontalView>
        <Text>Dancers: </Text>
        <View>
          {dancers}
        </View>
      </HorizontalView>
    </View>;
  }

  getSignup(prelim) {
    //TODO: Speed this up
    return this.props.signups.find(x => x.id == prelim.signupKey);
  }

  onSignupPressed(signup: Signup) {
    const prelims = [...this.state.prelims];
    const index = prelims.findIndex(x => x.signupKey == signup.id);
    prelims[index] = {
      ...prelims[index],
      auditioned: !prelims[index].auditioned,
    };
    this.setState(this.prelimsState(prelims));
  }

  renderRow(prelim: PrelimStatus, sectionId: string, rowId: string) {
    const signup = this.getSignup(prelim);
    if (!signup) {
      console.error('Missing signup for prelim', prelim, 'in list', this.props.signups);
      return null;
    }

    const rowIndex = parseInt(rowId, 10) + 1;
    const width = 50;
    const banner = prelim.auditioned ? <RibbonBanner text="Auditioned" width={width} /> : null;
    const style = null; // prelim.auditioned ? { backgroundColor: 'red' } : null;
    return <TouchableOpacity
        onPress={this.onSignupPressed}
      >
      <Card>
        <View>
          <HorizontalView>
            <Text style={{ marginRight: 10 }}>{rowIndex}:</Text>
            {this.renderSignup(signup)}
          </HorizontalView>
        </View>
        {banner}
      </Card>
    </TouchableOpacity>;
  }

  render() {
     return <ListView
      maxSwipeDistance={120}
      renderRow={this.renderRow}
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
