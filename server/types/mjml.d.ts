/**
 * MJML React JSX element types for email templating.
 */

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
  children?: React.ReactNode;
  key?: string | number;
}

declare global {
  namespace JSX {
    interface IntrinsicElements {
      'mj-section': MjmlElementProps;
      'mj-column': MjmlElementProps;
      'mj-group': MjmlElementProps;
      'mj-wrapper': MjmlElementProps;
      'mj-text': MjmlElementProps & {
        'font-size'?: string;
        'font-weight'?: string;
        'font-style'?: string;
        'line-height'?: string;
        color?: string;
        align?: 'left' | 'center' | 'right' | 'justify';
      };
      'mj-button': MjmlElementProps & {
        href?: string;
        color?: string;
        height?: string;
        'border-radius'?: string;
        align?: 'left' | 'center' | 'right';
      };
      'mj-image': MjmlElementProps & {
        src?: string;
        width?: string;
        height?: string;
        alt?: string;
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

export {};
