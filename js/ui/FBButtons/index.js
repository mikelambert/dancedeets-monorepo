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
import {
  injectIntl,
  defineMessages,
} from 'react-intl';

const messages = defineMessages({
  share: {
    id: 'buttons.share',
    defaultMessage: 'Share…',
    description: 'Button to share something on FB',
  },
});

class _FBShareButton extends React.Component {

  render() {
    return (
        <View style={{flexDirection: 'row'}}><Button
          icon={require('./images/facebook.png')}
          caption={this.props.intl.formatMessage(messages.share)}
          size="small"
          onPress={() => {
            ShareDialog.show(this.props.shareContent);
          }}
          {...this.props}
        /></View>
    );
  }
}
export const FBShareButton = injectIntl(_FBShareButton);
