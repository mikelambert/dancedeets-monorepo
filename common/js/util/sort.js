/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

export function sortString<T>(
  list: Array<T>,
  computeFunction: (value: T) => any
) {
  const sortValues = {};
  list.forEach(origValue => {
    const key = computeFunction(origValue);
    if (!sortValues[key]) {
      sortValues[key] = [];
    }
    sortValues[key].push(origValue);
  });
  const origSortedDeep = Object.keys(sortValues)
    .sort()
    .map(sortValue => sortValues[sortValue]);
  // Flatten the array of arrays into a single flattened array
  const origSorted = [].concat(...origSortedDeep);
  return origSorted;
}

export function sortNumber<T>(
  list: Array<T>,
  computeFunction: (value: T) => any
) {
  const sortValues = {};
  list.forEach(origValue => {
    const key = computeFunction(origValue);
    if (!sortValues[key]) {
      sortValues[key] = [];
    }
    sortValues[key].push(origValue);
  });
  const origSortedDeep = Object.keys(sortValues)
    .map(x => Number(x))
    .sort((a, b) => a - b)
    .map(sortValue => sortValues[sortValue]);
  // Flatten the array of arrays into a single flattened array
  const origSorted = [].concat(...origSortedDeep);
  return origSorted;
}
