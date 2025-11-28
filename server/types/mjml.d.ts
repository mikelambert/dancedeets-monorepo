/**
 * MJML React JSX element types for email templating.
 */

import 'react';

interface MjmlElementProps {
  'mj-class'?: string;
  padding?: string;
  'padding-left'?: string | number;
  'padding-right'?: string | number;
  'padding-top'?: string | number;
  'padding-bottom'?: string | number;
  'background-color'?: string;
  'background-url'?: string;
  'background-repeat'?: string;
  'container-background-color'?: string;
  'vertical-align'?: string;
  'font-family'?: string;
  width?: string;
  color?: string;
  align?: string;
  border?: string;
  children?: React.ReactNode;
  key?: string | number;
}

declare module 'react' {
  namespace JSX {
    interface IntrinsicElements {
      'mj-section': MjmlElementProps;
      'mj-column': MjmlElementProps;
      'mj-group': MjmlElementProps;
      'mj-wrapper': MjmlElementProps;
      'mj-container': MjmlElementProps;
      'mj-text': MjmlElementProps & {
        'font-size'?: string;
        'font-weight'?: string;
        'font-style'?: string;
        'line-height'?: string;
        height?: string;
      };
      'mj-button': MjmlElementProps & {
        href?: string;
        height?: string;
        'border-radius'?: string;
      };
      'mj-image': MjmlElementProps & {
        src?: string;
        height?: string;
        alt?: string;
        href?: string;
      };
      'mj-spacer': { height?: string; key?: string };
      'mj-table': MjmlElementProps;
      'mj-divider': MjmlElementProps & {
        'border-color'?: string;
        'border-width'?: string;
      };
      'mj-raw': { children?: React.ReactNode };
      'mj-body': MjmlElementProps;
      'mj-head': { children?: React.ReactNode };
      'mj-attributes': { children?: React.ReactNode };
      'mj-all': MjmlElementProps;
      'mj-class': { name?: string } & MjmlElementProps;
      'mj-preview': { children?: React.ReactNode };
      'mj-style': { children?: React.ReactNode; inline?: string };
      mjml: { children?: React.ReactNode };
    }
  }
}
