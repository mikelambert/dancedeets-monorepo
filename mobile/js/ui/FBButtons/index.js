/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { View } from 'react-native';
import type { ShareContent } from 'react-native-fbsdk/js/models/FBShareContent';
import { ShareDialog } from 'react-native-fbsdk';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import Button from '../Button';

const messages = defineMessages({
  share: {
    id: 'buttons.share',
    defaultMessage: 'Share…',
    description: 'Button to share something on FB',
  },
});

class _FBShareButton extends React.Component {
  props: {
    intl: intlShape,
    shareContent: ShareContent,
  };

  render() {
    return (
      <View style={{ flexDirection: 'row' }}>
        <Button
          icon={require('./images/facebook.png')}
          caption={this.props.intl.formatMessage(messages.share)}
          size="small"
          onPress={() => {
            ShareDialog.show(this.props.shareContent);
          }}
          {...this.props}
        />
      </View>
    );
  }
}
export const FBShareButton = injectIntl(_FBShareButton);
