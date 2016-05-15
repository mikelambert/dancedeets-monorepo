/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React, {
  ActivityIndicatorIOS,
  Platform,
  ProgressBarAndroid,
} from 'react-native';

export default class ProgressSpinner extends React.Component {
  render() {
    if (Platform.OS == 'android') {
      return <ProgressBarAndroid indeterminate={true} styleAttr="large" />;
    } else {
      return <ActivityIndicatorIOS color="white" size="large"/>;
    }
  }
}
