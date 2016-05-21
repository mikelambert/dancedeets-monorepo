/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React from 'react';
import { View } from 'react-native';
import { ShareDialog } from 'react-native-fbsdk';
import Button from '../Button';

export class FBShareButton extends React.Component {

  render() {
    return (
        <View style={{flexDirection: 'row'}}><Button
          icon={require('./images/facebook.png')}
          caption="Share"
          size="small"
          onPress={() => {
            console.log(this.props.shareContent);
            ShareDialog.show(this.props.shareContent);
          }}
          {...this.props}
        /></View>
    );
  }
}
