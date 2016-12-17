/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

function domClass(className) {
  return [].slice.call(document.getElementsByClassName(className));
}

function domQuery(query) {
  return [].slice.call(document.querySelectorAll(query));
}

export function queryOn(query: string, event: string, fn: (e: Event) => void) {
  domQuery(query).forEach(x => x.addEventListener(event, fn));
}

export function queryOff(query: string, event: string, fn: (e: Event) => void) {
  domQuery(query).forEach(x => x.removeEventListener(event, fn));
}
