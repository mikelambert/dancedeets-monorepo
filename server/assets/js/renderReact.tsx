/**
 * Copyright 2016 DanceDeets.
 */

import 'core-js/stable';
import 'regenerator-runtime/runtime';
import * as React from 'react';
import { createRoot, Root } from 'react-dom/client';
import { AppContainer } from 'react-hot-loader';

// Store root instances for hot module replacement
const roots = new Map<Element, Root>();

export default function renderReact(
  Component: React.ComponentType<Record<string, unknown>>,
  props?: Record<string, unknown>
): void {
  const container = document.getElementById(window._REACT_ID);
  if (!container) {
    console.error(`Could not find element with id: ${window._REACT_ID}`);
    return;
  }

  // Reuse existing root for hot module replacement, or create new one
  let root = roots.get(container);
  if (!root) {
    root = createRoot(container);
    roots.set(container, root);
  }

  root.render(
    <AppContainer>
      <Component {...window._REACT_PROPS} {...props} />
    </AppContainer>
  );
}
