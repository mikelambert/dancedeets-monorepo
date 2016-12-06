import StackTrace from 'stacktrace-js';
import { StackdriverErrorReporter } from 'stackdriver-errors-js';

window.StackTrace = StackTrace;

const errorHandler = new StackdriverErrorReporter();
errorHandler.start({
  key: 'AIzaSyAvvrWfamjBD6LqCURkATAWEovAoBm1xNQ', // Website Key (referrer-locked)
  projectId: '911140565156',
});
