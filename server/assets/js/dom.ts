/**
 * Copyright 2016 DanceDeets.
 */

function domQuery(query: string): Element[] {
  return [].slice.call(document.querySelectorAll(query));
}

export function queryOn(
  query: string,
  event: string,
  fn: (e: Event) => void
): void {
  domQuery(query).forEach(x => x.addEventListener(event, fn));
}

export function queryOff(
  query: string,
  event: string,
  fn: (e: Event) => void
): void {
  domQuery(query).forEach(x => x.removeEventListener(event, fn));
}
