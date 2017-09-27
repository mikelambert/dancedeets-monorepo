/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';

export class EmailWrapper extends React.Component {
  props: {
    header: string,
    footer: string,
    children: React.Element<*>,
  };

  render() {
    return (
      <mjml>
        <mj-head>
          <mj-attributes>
            <mj-all
              padding="0"
              color="#000000"
              font-size="12px"
              line-height="20px"
              font-family="Ubuntu, Helvetica, Arial, sans-serif"
            />
            <mj-class name="header" font-size="18px" line-height="26px" />
          </mj-attributes>
        </mj-head>
        <mj-body>
          <mj-container background-color="#D0D0F0">
            <mj-section full-width="full-width" padding="10px 25px">
              <mj-group>
                <mj-column>
                  <mj-text>{this.props.header}</mj-text>
                </mj-column>
              </mj-group>
            </mj-section>
            <mj-section full-width="full-width">
              <mj-column>
                <mj-image
                  src="https://www.dancedeets.com/images/mail-top.png"
                  alt=""
                />
              </mj-column>
            </mj-section>
            <mj-section background-color="#222337" padding="0">
              <mj-column width="40%">
                <mj-image
                  align="center"
                  src="https://www.dancedeets.com/dist-400780539943311269/img/deets-head-and-title-on-black@2x.png"
                  alt="logo"
                  padding="0 0 30px 0"
                />
              </mj-column>
            </mj-section>

            {this.props.children}

            <mj-section>
              <mj-column>
                <mj-image
                  src="https://www.dancedeets.com/images/mail-bottom.png"
                  alt=""
                  align="center"
                  border="none"
                  width="600"
                  container-background-color="transparent"
                />
              </mj-column>
            </mj-section>
            <mj-section full-width="full-width" padding="20px">
              <mj-column>
                <mj-text align="center">{this.props.footer}</mj-text>
              </mj-column>
            </mj-section>
          </mj-container>
        </mj-body>
      </mjml>
    );
  }
}
