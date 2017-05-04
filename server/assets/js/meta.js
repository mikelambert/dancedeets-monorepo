/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

export function generateMetaTags(
  title: string,
  url: string,
  thumbnail: string
) {
  return [
    { name: 'twitter:site', content: '@dancedeets' },
    { name: 'twitter:creator', content: '@dancedeets' },
    { name: 'twitter:title', content: title },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:image:src', content: thumbnail },
    { property: 'og:title', content: title },
    { property: 'og:type', content: 'website' },
    { property: 'og:url', content: url },
    { property: 'og:site_name', content: 'DanceDeets' },
    { property: 'og:image', content: thumbnail },
  ];
}
