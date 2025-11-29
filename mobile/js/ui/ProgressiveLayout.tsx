/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { FlatList, ListRenderItemInfo } from 'react-native';

interface Props {
  children: React.ReactElement[];
  [key: string]: any;
}

interface DataItem {
  key: string;
  element: React.ReactElement;
}

export default class ProgressiveLayout extends React.Component<Props> {
  renderItem = ({ item }: ListRenderItemInfo<DataItem>): React.ReactElement => {
    return item.element;
  };

  keyExtractor = (item: DataItem): string => {
    return item.key;
  };

  render() {
    const { children, ...otherProps } = this.props;

    // Convert children to data array with keys
    const data: DataItem[] = React.Children.map(children, (child, index) => ({
      key: String(index),
      element: child,
    })) || [];

    return (
      <FlatList
        data={data}
        renderItem={this.renderItem}
        keyExtractor={this.keyExtractor}
        initialNumToRender={1}
        maxToRenderPerBatch={1}
        windowSize={21}
        indicatorStyle="white"
        {...otherProps}
      />
    );
  }
}
