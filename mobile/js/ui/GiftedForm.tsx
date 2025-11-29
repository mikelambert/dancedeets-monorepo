/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { View } from 'react-native';
import { GiftedForm, SubmitWidget } from 'react-native-gifted-form';
import { purpleColors, yellowColors } from '../Colors';
import Button from './Button';
import { defaultFont } from './DDText';

interface MyGiftedSubmitWidgetProps {
  title?: string;
  isDisabled?: boolean;
  activityIndicatorColor?: string;
  onSubmit?: (
    isValid: boolean,
    values: object,
    validationResults: any,
    postSubmit?: ((errors?: string[]) => void) | null,
    modalNavigator?: any
  ) => void | Promise<void>;
}

export class MyGiftedSubmitWidget extends (SubmitWidget as any) {
  props!: MyGiftedSubmitWidgetProps;
  state!: { isLoading: boolean };

  render() {
    return (
      <View>
        <Button
          style={this.getStyle('submitButton')}
          textStyle={this.getStyle('textSubmitButton')}
          disabledStyle={this.getStyle('disabledSubmitButton')}
          isLoading={this.state.isLoading}
          isDisabled={this.props.isDisabled}
          activityIndicatorColor={this.props.activityIndicatorColor}
          onPress={() => this._doSubmit()}
          caption={this.props.title || 'Submit'}
        />
      </View>
    );
  }
}

export class MyGiftedForm extends React.Component<any> {
  render() {
    return (
      <GiftedForm
        scrollEnabled={false}
        formName="signupForm"
        clearOnClose={false}
        formStyles={{
          containerView: { backgroundColor: 'transparent' },
          TextInputWidget: {
            rowContainer: {
              backgroundColor: 'transparent',
              borderColor: purpleColors[1],
            },
            underlineIdle: {
              borderColor: purpleColors[2],
            },
            underlineFocused: {
              borderColor: yellowColors[2],
            },
            textInputTitleInline: defaultFont,
            textInputTitle: defaultFont,
            textInput: Object.assign({}, defaultFont, {
              backgroundColor: purpleColors[1],
            }),
            textInputInline: Object.assign({}, defaultFont, {
              backgroundColor: purpleColors[1],
            }),
          },
          SubmitWidget: {
            submitButton: {
              backgroundColor: purpleColors[3],
            },
          },
        }}
        {...this.props}
      />
    );
  }
}
