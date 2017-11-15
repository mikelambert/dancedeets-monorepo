/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';
import { View } from 'react-native';
import type { ShareContent } from 'react-native-fbsdk/js/models/FBShareContent';
import { ShareDialog } from 'react-native-fbsdk';
import { injectIntl, intlShape, defineMessages } from 'react-intl';
import { Event } from 'dancedeets-common/js/events/models';
import Button from '../Button';
import { track, trackWithEvent } from '../../store/track';

const messages = defineMessages({
  share: {
    id: 'buttons.share',
    defaultMessage: 'Share…',
    description: 'Button to share something on FB',
  },
});

class _FBShareButton extends React.Component {
  props: {
    shareContent: ShareContent,
    event?: Event,

    // Self-managed props
    intl: intlShape,
  };

  render() {
    return (
      <View style={{ flexDirection: 'row' }}>
        <Button
          icon={require('./images/facebook.png')}
          caption={this.props.intl.formatMessage(messages.share)}
          size="small"
          onPress={() => {
            if (this.props.event) {
              trackWithEvent('FBShare', this.props.event);
            } else {
              track('FBShare');
            }
            ShareDialog.show(this.props.shareContent);
          }}
          {...this.props}
        />
      </View>
    );
  }
}
export const FBShareButton = injectIntl(_FBShareButton);
