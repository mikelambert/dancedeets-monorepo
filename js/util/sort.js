/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

export default function sort<T>(list: Array<T>, computeFunction: (value: T) => any) {
  const sortValues = {};
  for (let origValue of list) {
    const key = computeFunction(origValue);
    if (!sortValues[key]) {
      sortValues[key] = [];
    }
    sortValues[key].push(origValue);
  }
  const origSortedDeep = Object.keys(sortValues).sort().map((sortValue) => sortValues[sortValue]);
  // Flatten the array of arrays into a single flattened array
  const origSorted = [].concat.apply([], origSortedDeep);
  return origSorted;
}
