/**
 * AMP Elements JSX declarations.
 * This module augments React's JSX namespace to add AMP element types.
 */
import 'react';

declare module 'react' {
  namespace JSX {
    interface IntrinsicElements {
      'amp-ad': React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          layout?: string;
          width?: string | number;
          height?: string | number;
          type?: string;
          'data-ad-client'?: string;
          'data-ad-slot'?: string;
        },
        HTMLElement
      >;
      'amp-img': React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          src?: string | number;
          srcset?: string;
          srcSet?: string;
          alt?: string;
          attribution?: string;
          width?: string | number | null;
          height?: string | number | null;
          layout?: string;
          sizes?: string;
          fallback?: boolean;
          placeholder?: boolean;
        },
        HTMLElement
      >;
      'amp-youtube': React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          'data-videoid'?: string;
          layout?: string;
          width?: string | number;
          height?: string | number;
        },
        HTMLElement
      >;
      'amp-facebook': React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          'data-href'?: string;
          layout?: string;
          width?: string | number;
          height?: string | number;
        },
        HTMLElement
      >;
      'amp-facebook-like': React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          'data-href'?: string;
          layout?: string;
          width?: string | number;
          height?: string | number;
        },
        HTMLElement
      >;
      'amp-iframe': React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          src?: string;
          layout?: string;
          width?: string | number;
          height?: string | number;
          frameborder?: string | number;
          allowfullscreen?: string;
          sandbox?: string;
        },
        HTMLElement
      >;
    }
  }
}
