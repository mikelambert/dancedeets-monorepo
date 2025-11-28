/**
 * Copyright 2016 DanceDeets.
 */

const exportedIcons = {
  'clock-o': true,
  'map-marker': true,
} as const;

export type ExportedIconsEnum = keyof typeof exportedIcons;

export default Object.keys(exportedIcons);
