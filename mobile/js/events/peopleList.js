/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  StyleSheet,
  TouchableHighlight,
  TouchableOpacity,
  View,
} from 'react-native';
import { connect } from 'react-redux';
import Collapsible from 'react-native-collapsible';
import Icon from 'react-native-vector-icons/Ionicons';
import type {
  PeopleListing,
  StylePersonLookup,
} from 'dancedeets-common/js/events/search';
import { formatStartDateOnly } from 'dancedeets-common/js/dates';
import { BlurredImage, HorizontalView, Text } from '../ui';
import type { State } from '../reducers/search';
import { openUserId } from '../util/fb';
import { linkColor } from '../Colors';

class PersonList extends React.Component {
  props: {
    subtitle: string,
    people: StylePersonLookup,
  };

  state: {
    category: string,
  };

  constructor(props) {
    super(props);
    this.state = {
      category: '',
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
    const peopleList = this.props.people[this.state.category].slice(0, 10);
    // const categories = this.props.categoryOrder.filter(x => x === '' || this.props.people[x]);
    // {categories.map(x => <option key={x} value={x}>{x || 'Overall'}</option>)}

    if (!peopleList.length) {
      return null;
    }

    const id = peopleList[0].id;
    const url = `https://graph.facebook.com/${id}/picture?type=large`;
    return (
      <BlurredImage source={{ uri: url }}>
        <Text style={{ fontStyle: 'italic' }}>{this.props.subtitle}:</Text>
        {peopleList.map(x => this.renderLink(x))}
      </BlurredImage>
    );
  }
}

class HeaderCollapsible extends React.Component {
  props: {
    defaultCollapsed: boolean,
    title: string,
    children?: React.Element<*>,
    underlayColor?: string,
  };

  state: {
    collapsed: boolean,
  };

  _toggle() {
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
    return (
      <View>
        <TouchableHighlight
          onPress={this._toggle}
          underlayColor={this.props.underlayColor}
        >
          <View style={styles.sectionHeader}>
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
        </TouchableHighlight>
        <Collapsible collapsed={this.state.collapsed}>
          {this.props.children}
        </Collapsible>
      </View>
    );
  }
}

class _PeopleView extends React.Component {
  props: {
    people: PeopleListing,
    headerStyle: View.propTypes,

    // Self-managed props
    search: State,
  };

  render() {
    if (this.props.search.error) {
      return null;
    }
    // Keep in sync with web?
    const defaultCollapsed = !(this.props.search.response.results.length < 10);
    return (
      <View>
        <HeaderCollapsible
          title="Nearby Promoters"
          defaultCollapsed={defaultCollapsed}
        >
          <PersonList
            subtitle="If you want to organize an event, work with these folks"
            people={this.props.people.ADMIN}
          />
        </HeaderCollapsible>
        <HeaderCollapsible
          title="Nearby Dancers"
          defaultCollapsed={defaultCollapsed}
          style={this.props.headerStyle}
        >
          <PersonList
            subtitle="If you want to connect with the dance scene, hit these folks up"
            people={this.props.people.ATTENDEE}
            defaultCollapsed={defaultCollapsed}
          />
        </HeaderCollapsible>
      </View>
    );
  }
}
const PeopleView = connect(state => ({
  search: state.search,
}))(_PeopleView);

export default PeopleView;

const styles = StyleSheet.create({
  rowLink: {
    color: linkColor,
  },
});
