/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import {
  ActivityIndicator,
  StyleSheet,
  StyleProp,
  ViewStyle,
  TouchableOpacity,
  View,
} from 'react-native';
import { connect } from 'react-redux';
import Icon from 'react-native-vector-icons/Ionicons';
import { injectIntl, IntlShape, defineMessages } from 'react-intl';
import {
  PeopleListing,
  StylePersonLookup,
} from 'dancedeets-common/js/events/search';
import { messages } from 'dancedeets-common/js/events/people';
import { Collapsible, HorizontalView, semiNormalize, Text } from '../ui';
import { State } from '../reducers/search';
import { openUserId } from '../util/fb';
import { linkColor } from '../Colors';

interface PersonListProps {
  subtitle: string;
  people: StylePersonLookup;

  // Self-managed props
  intl: IntlShape;
}

interface PersonListState {
  category: string;
}

class _PersonList extends React.Component<PersonListProps, PersonListState> {
  constructor(props: PersonListProps) {
    super(props);
    this.state = {
      category: 'Street Dance',
    };
  }

  renderLink(user: { id: string; name: string }) {
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

interface HeaderCollapsibleProps {
  defaultCollapsed: boolean;
  title: string;
  children: React.ReactNode;
  underlayColor?: string;
  onPress?: () => void | Promise<void>;
}

interface HeaderCollapsibleState {
  collapsed: boolean;
}

class HeaderCollapsible extends React.Component<
  HeaderCollapsibleProps,
  HeaderCollapsibleState
> {
  _toggle() {
    if (this.props.onPress) {
      this.props.onPress();
    }
    this.setState({ collapsed: !this.state.collapsed });
  }

  constructor(props: HeaderCollapsibleProps) {
    super(props);
    this.state = { collapsed: !!props.defaultCollapsed };
    this._toggle = this._toggle.bind(this);
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

interface LoadingProps {
  // Self-managed props
  intl: IntlShape;
}

class _Loading extends React.Component<LoadingProps> {
  render() {
    return <ActivityIndicator style={{ marginLeft: 20, marginBottom: 20 }} />;
  }
}

const Loading = injectIntl(_Loading);

interface OrganizerViewProps {
  defaultCollapsed: boolean;
  headerStyle: StyleProp<ViewStyle>;
  people: StylePersonLookup | null;
  onPress?: () => void | Promise<void>;

  // Self-managed props
  intl: IntlShape;
}

class _OrganizerView extends React.PureComponent<OrganizerViewProps> {
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

interface AttendeeViewProps {
  defaultCollapsed: boolean;
  headerStyle: StyleProp<ViewStyle>;
  people: StylePersonLookup | null;
  onPress?: () => void | Promise<void>;

  // Self-managed props
  intl: IntlShape;
}

export class _AttendeeView extends React.PureComponent<AttendeeViewProps> {
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
