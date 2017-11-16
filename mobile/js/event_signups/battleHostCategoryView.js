/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { FlatList, TouchableOpacity, View } from 'react-native';
import { injectIntl } from 'react-intl';
import { Card, HorizontalView, RibbonBanner, Text } from '../ui';
import type { BattleCategory, PrelimStatus, Signup } from './models';
import { getCategorySignups } from './models';

class _TeamList extends React.Component<
  {
    signups: Array<Signup>,
  },
  {
    prelims: Array<PrelimStatus>,
  }
> {
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

  onSignupPressed(prelim: PrelimStatus) {
    const prelims = [...this.state.prelims];
    const index = prelims.findIndex(x => x.signupKey === prelim.signupKey);
    prelims[index] = {
      ...prelims[index],
      auditioned: !prelims[index].auditioned,
    };
    this.setState(this.prelimsState(prelims));
  }

  getSignup(prelim) {
    // TODO: Speed this up
    return this.props.signups.find(x => x.id === prelim.signupKey);
  }

  prelimsState(prelims) {
    return {
      prelims,
    };
  }

  renderSignup(signup: Signup) {
    const dancers = (signup.dancers || [])
      .map((x, index) => <Text key={x.name}>{x.name}</Text>);
    return (
      <View>
        <HorizontalView>
          <Text>Team: </Text>
          <Text>{signup.teamName}</Text>
        </HorizontalView>
        <HorizontalView>
          <Text>Dancers: </Text>
          <View>{dancers}</View>
        </HorizontalView>
      </View>
    );
  }

  renderRow(row: { item: { index: number, prelim: PrelimStatus } }) {
    const { prelim, index } = row.item;
    const signup = this.getSignup(prelim);
    if (!signup) {
      console.error(
        'Missing signup for prelim',
        prelim,
        'in list',
        this.props.signups
      );
      return null;
    }

    const width = 50;
    const banner = prelim.auditioned ? (
      <RibbonBanner text="Auditioned" width={width} />
    ) : null;
    return (
      <TouchableOpacity onPress={() => this.onSignupPressed(prelim)}>
        <Card>
          <View>
            <HorizontalView>
              <Text style={{ marginRight: 10 }}>{index + 1}:</Text>
              {this.renderSignup(signup)}
            </HorizontalView>
          </View>
          {banner}
        </Card>
      </TouchableOpacity>
    );
  }

  render() {
    return (
      <FlatList
        maxSwipeDistance={120}
        renderItem={this.renderRow}
        data={this.state.prelims}
        onScroll={e => {}}
      />
    );
  }
}
const TeamList = injectIntl(_TeamList);

class _BattleHostCategoryView extends React.Component<{
  category: BattleCategory,
}> {
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
            <Text>{signups.length} competitors:</Text>
          </View>
        )}
      />
    );
  }
}
const BattleHostCategoryView = injectIntl(_BattleHostCategoryView);

export default BattleHostCategoryView;
