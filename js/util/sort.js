/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

export default function sort<T>(list: Array<T>, computeFunction: (value: T) => any) {
  const sortValues = {};
  for (let origValue of list) {
    sortValues[computeFunction(origValue)] = origValue;
  }
  const origSorted = Object.keys(sortValues).sort().map((sortValue) => sortValues[sortValue]);
  return origSorted;
}
