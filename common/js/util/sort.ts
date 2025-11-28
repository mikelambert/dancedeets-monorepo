/**
 * Copyright 2016 DanceDeets.
 */

export function sortString<T>(
  list: Array<T>,
  computeFunction: (value: T) => string | number
): Array<T> {
  const sortValues: Record<string, Array<T>> = {};
  list.forEach(origValue => {
    const key = String(computeFunction(origValue));
    if (!sortValues[key]) {
      sortValues[key] = [];
    }
    sortValues[key].push(origValue);
  });
  const origSortedDeep = Object.keys(sortValues)
    .sort()
    .map(sortValue => sortValues[sortValue]);
  // Flatten the array of arrays into a single flattened array
  const origSorted = ([] as Array<T>).concat(...origSortedDeep);
  return origSorted;
}

export function sortNumber<T>(
  list: Array<T>,
  computeFunction: (value: T) => number
): Array<T> {
  const sortValues: Record<number, Array<T>> = {};
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
  const origSorted = ([] as Array<T>).concat(...origSortedDeep);
  return origSorted;
}
