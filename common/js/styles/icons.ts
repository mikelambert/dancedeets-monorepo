/**
 * Copyright 2016 DanceDeets.
 */

// Image imports - bundlers (webpack, metro, esbuild) will handle these appropriately
import breakIcon from './images/break.png';
import hiphopIcon from './images/hiphop.png';
import popIcon from './images/pop.png';
import lockIcon from './images/lock.png';
import houseIcon from './images/house.png';
import krumpIcon from './images/krump.png';
import otherIcon from './images/other.png';

const icons: Record<string, unknown> = {
  break: breakIcon,
  hiphop: hiphopIcon,
  pop: popIcon,
  lock: lockIcon,
  house: houseIcon,
  krump: krumpIcon,
  other: otherIcon,
};

export default icons;
