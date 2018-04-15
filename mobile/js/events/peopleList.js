/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import {
  ActivityIndicator,
  StyleSheet,
  TouchableOpacity,
  View,
  ViewPropTypes,
} from 'react-native';
import { connect } from 'react-redux';
import Icon from 'react-native-vector-icons/Ionicons';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import type {
  PeopleListing,
  StylePersonLookup,
} from 'dancedeets-common/js/events/search';
import { messages } from 'dancedeets-common/js/events/people';
import { Collapsible, HorizontalView, semiNormalize, Text } from '../ui';
import type { State } from '../reducers/search';
import { openUserId } from '../util/fb';
import { linkColor } from '../Colors';

class _PersonList extends React.Component<
  {
    subtitle: string,
    people: StylePersonLookup,

    // Self-managed props
    intl: intlShape,
  },
  {
    category: string,
  }
> {
  constructor(props) {
    super(props);
    this.state = {
      category: 'Street Dance',
    };
  }

  renderLink(user) {
    return (
      <HorizontalView key={user.id}>
        <Text> – </Text>
        <TouchableOpacity key={user.id} onPress={() => openUserId(user.id)}>
          <Text style={[styles.rowLink]}>{user.name}</Text>
        </TouchableOpacity>
      </HorizontalView>
    );
  }

  render() {
    if (!this.props.people[this.state.category]) {
      return (
        <Text style={{ marginLeft: 20, marginBottom: 10 }}>
          {this.props.intl.formatMessage(messages.nooneNearby)}
        </Text>
      );
    }
    const peopleList = this.props.people[this.state.category].slice(0, 10);
    // const categories = this.props.categoryOrder.filter(x => this.props.people[x]);
    // {categories.map(x => <option key={x} value={x}>{x || 'Overall'}</option>)}

    if (!peopleList.length) {
      return null;
    }

    const id = peopleList[0].id;
    const url = `https://graph.facebook.com/${id}/picture?type=large`;
    return (
      <View>
        <Text style={{ fontStyle: 'italic' }}>{this.props.subtitle}:</Text>
        {peopleList.map(x => this.renderLink(x))}
      </View>
    );
  }
}
const PersonList = injectIntl(_PersonList);

class HeaderCollapsible extends React.Component<
  {
    defaultCollapsed: boolean,
    title: string,
    children: React.Node,
    underlayColor?: string,
    onPress?: () => void | Promise<void>,
  },
  {
    collapsed: boolean,
  }
> {
  _toggle() {
    if (this.props.onPress) {
      this.props.onPress();
    }
    this.setState({ collapsed: !this.state.collapsed });
  }

  constructor(props) {
    super(props);
    this.state = { collapsed: !!props.defaultCollapsed };
    (this: any)._toggle = this._toggle.bind(this);
  }

  render() {
    const iconName = this.state.collapsed
      ? 'md-arrow-dropright'
      : 'md-arrow-dropdown';
    // The TouchableHighlight needs a native component that takes a ref.
    // Unfortunately the stateless HorizontalView component cannot take a ref, so we have a View wrapper.
    return (
      <View>
        <TouchableOpacity
          onPress={this._toggle}
          underlayColor={this.props.underlayColor}
        >
          <View
            style={{
              justifyContent: 'center',
              height: semiNormalize(50),
            }}
          >
            <HorizontalView>
              <View
                style={{
                  width: 20,
                  height: 20,
                  alignItems: 'center',
                  alignSelf: 'center',
                }}
              >
                <Icon name={iconName} size={15} color="#FFF" />
              </View>
              <Text>{this.props.title}</Text>
            </HorizontalView>
          </View>
        </TouchableOpacity>
        <Collapsible collapsed={this.state.collapsed} align="center">
          {this.props.children}
        </Collapsible>
      </View>
    );
  }
}

class _Loading extends React.Component<{
  // Self-managed props
  intl: intlShape,
}> {
  render() {
    return <ActivityIndicator style={{ marginLeft: 20, marginBottom: 20 }} />;
  }
}
const Loading = injectIntl(_Loading);

class _OrganizerView extends React.PureComponent<{
  defaultCollapsed: boolean,
  headerStyle: ViewPropTypes.style,
  people: ?StylePersonLookup,
  onPress?: () => void | Promise<void>,

  // Self-managed props
  intl: intlShape,
}> {
  render() {
    const personList = this.props.people ? (
      <PersonList
        subtitle={this.props.intl.formatMessage(
          messages.nearbyPromotersMessage
        )}
        people={this.props.people}
      />
    ) : (
      <Loading />
    );

    return (
      <HeaderCollapsible
        title={this.props.intl.formatMessage(messages.nearbyPromoters)}
        defaultCollapsed={this.props.defaultCollapsed}
        style={this.props.headerStyle}
        onPress={this.props.onPress}
      >
        {personList}
      </HeaderCollapsible>
    );
  }
}
export const OrganizerView = injectIntl(_OrganizerView);

export class _AttendeeView extends React.PureComponent<{
  defaultCollapsed: boolean,
  headerStyle: ViewPropTypes.style,
  people: ?StylePersonLookup,
  onPress?: () => void | Promise<void>,

  // Self-managed props
  intl: intlShape,
}> {
  render() {
    const personList = this.props.people ? (
      <PersonList
        subtitle={this.props.intl.formatMessage(messages.nearbyDancersMessage)}
        people={this.props.people}
      />
    ) : (
      <Loading />
    );

    return (
      <HeaderCollapsible
        title={this.props.intl.formatMessage(messages.nearbyDancers)}
        defaultCollapsed={this.props.defaultCollapsed}
        style={this.props.headerStyle}
        onPress={this.props.onPress}
      >
        {personList}
      </HeaderCollapsible>
    );
  }
}
export const AttendeeView = injectIntl(_AttendeeView);

const styles = StyleSheet.create({
  rowLink: {
    color: linkColor,
  },
});
