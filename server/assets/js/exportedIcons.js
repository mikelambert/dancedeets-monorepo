/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

const exportedIcons = {
  'clock-o': true,
  'map-marker': true,
};
export type ExportedIconsEnum = $Keys<typeof exportedIcons>;

export default Object.keys(exportedIcons);
