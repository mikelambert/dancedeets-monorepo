/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { View } from 'react-native';
import { ShareContent } from 'react-native-fbsdk';
import { ShareDialog } from 'react-native-fbsdk';
import { injectIntl, IntlShape, defineMessages } from 'react-intl';
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

interface Props {
  shareContent: ShareContent;
  event?: Event;
  intl: IntlShape;
}

class _FBShareButton extends React.Component<Props> {
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
