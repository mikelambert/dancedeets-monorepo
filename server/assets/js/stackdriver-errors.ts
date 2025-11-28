/**
 * Copyright 2016 DanceDeets.
 */

/// <reference path="../../types/window.d.ts" />

import StackTrace from 'stacktrace-js';
import { StackdriverErrorReporter } from 'stackdriver-errors-js';

declare global {
  interface Window {
    StackTrace: typeof StackTrace;
  }
}

window.StackTrace = StackTrace;

const errorHandler = new StackdriverErrorReporter();
if (window.prodMode) {
  errorHandler.start({
    key: 'AIzaSyAvvrWfamjBD6LqCURkATAWEovAoBm1xNQ', // Website Key (referrer-locked)
    projectId: '911140565156',
  });
}
