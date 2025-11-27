/**
 * Type declarations for packages without @types.
 */

// react-twitter-widgets
declare module 'react-twitter-widgets' {
  import * as React from 'react';

  export interface ShareProps {
    url: string;
    options?: Record<string, unknown>;
  }

  export class Share extends React.Component<ShareProps> {}
}

// react-hot-loader
declare module 'react-hot-loader' {
  import * as React from 'react';

  export function hot<T extends React.ComponentType<unknown>>(
    module: NodeModule
  ): (component: T) => T;

  export class AppContainer extends React.Component<{
    children?: React.ReactNode;
  }> {}
}

// react-measure
declare module 'react-measure' {
  import * as React from 'react';

  export interface ContentRect {
    bounds?: {
      width: number;
      height: number;
      top: number;
      left: number;
      bottom: number;
      right: number;
    };
    scroll?: {
      width: number;
      height: number;
      top: number;
      left: number;
    };
    offset?: {
      width: number;
      height: number;
      top: number;
      left: number;
    };
    client?: {
      width: number;
      height: number;
      top: number;
      left: number;
    };
    margin?: {
      top: number;
      left: number;
      bottom: number;
      right: number;
    };
    entry?: ResizeObserverEntry;
  }

  export interface MeasureProps {
    bounds?: boolean;
    scroll?: boolean;
    offset?: boolean;
    client?: boolean;
    margin?: boolean;
    innerRef?: (ref: HTMLElement | null) => void;
    onResize?: (contentRect: ContentRect) => void;
    children: (props: { measureRef: React.RefCallback<HTMLElement> }) => React.ReactNode;
  }

  export default class Measure extends React.Component<MeasureProps> {}
}

// react-intl augmentation
declare module 'react-intl' {
  import * as React from 'react';

  export interface MessageDescriptor {
    id: string;
    defaultMessage?: string;
    description?: string;
  }
  export const FormattedMessage: React.ComponentType<MessageDescriptor & { values?: Record<string, unknown> }>;
  export const injectIntl: <P extends { intl: unknown }>(component: React.ComponentType<P>) => React.ComponentType<Omit<P, 'intl'>>;
  export function defineMessages<T extends Record<string, MessageDescriptor>>(messages: T): T;
}

// ReactDOM.render for older React (deprecated in React 18 types)
declare module 'react-dom' {
  import * as React from 'react';

  export function render(
    element: React.ReactElement,
    container: Element | null,
    callback?: () => void
  ): React.Component | Element | void;
  export function hydrate(
    element: React.ReactElement,
    container: Element | null,
    callback?: () => void
  ): React.Component | Element | void;
}

// linkify-it
declare module 'linkify-it' {
  interface Match {
    schema: string;
    index: number;
    lastIndex: number;
    raw: string;
    text: string;
    url: string;
  }

  interface LinkifyIt {
    tlds(list: string[]): LinkifyIt;
    match(text: string): Match[] | null;
    test(text: string): boolean;
  }

  function linkify(): LinkifyIt;
  export = linkify;
}

// tlds
declare module 'tlds' {
  const tlds: string[];
  export default tlds;
}

// exenv
declare module 'exenv' {
  export const canUseDOM: boolean;
  export const canUseWorkers: boolean;
  export const canUseEventListeners: boolean;
  export const canUseViewport: boolean;
}

// react-helmet
declare module 'react-helmet' {
  import * as React from 'react';

  interface HelmetProps {
    base?: object;
    bodyAttributes?: object;
    defaultTitle?: string;
    defer?: boolean;
    encodeSpecialCharacters?: boolean;
    htmlAttributes?: object;
    link?: object[];
    meta?: object[];
    noscript?: object[];
    onChangeClientState?: (newState: object, addedTags: object, removedTags: object) => void;
    script?: object[];
    style?: object[];
    title?: string;
    titleAttributes?: object;
    titleTemplate?: string;
    children?: React.ReactNode;
  }

  export default class Helmet extends React.Component<HelmetProps> {
    static peek(): object;
    static rewind(): object;
    static renderStatic(): object;
  }
}

// raven-js
declare module 'raven-js' {
  interface RavenOptions {
    environment?: string;
    release?: string;
    tags?: Record<string, string>;
    extra?: Record<string, unknown>;
  }

  interface Raven {
    config(dsn: string, options?: RavenOptions): Raven;
    install(): Raven;
    captureException(error: Error | unknown, options?: object): void;
    captureMessage(message: string, options?: object): void;
    setUserContext(user?: object): void;
  }

  const raven: Raven;
  export default raven;
}

// react-lazyload
declare module 'react-lazyload' {
  import * as React from 'react';

  interface LazyLoadProps {
    height?: number | string;
    once?: boolean;
    offset?: number | number[];
    scroll?: boolean;
    resize?: boolean;
    overflow?: boolean;
    placeholder?: React.ReactNode;
    debounce?: number | boolean;
    throttle?: number | boolean;
    children?: React.ReactNode;
  }

  export default class LazyLoad extends React.Component<LazyLoadProps> {}
}

// console-polyfill
declare module 'console-polyfill' {}

// jquery.smartbanner
declare module 'jquery.smartbanner' {}

// bootstrap modules
declare module 'bootstrap/js/alert' {}
declare module 'bootstrap/js/modal' {}
declare module 'bootstrap/js/collapse' {}
declare module 'bootstrap/js/dropdown' {}
declare module 'bootstrap/js/transition' {}

// eventemitter3
declare module 'eventemitter3' {
  class EventEmitter {
    constructor();
    on(event: string, listener: (...args: unknown[]) => void): this;
    once(event: string, listener: (...args: unknown[]) => void): this;
    off(event: string, listener?: (...args: unknown[]) => void): this;
    emit(event: string, ...args: unknown[]): boolean;
    removeAllListeners(event?: string): this;
  }
  export = EventEmitter;
}

// universal-cookie
declare module 'universal-cookie' {
  interface CookieSetOptions {
    path?: string;
    expires?: Date;
    maxAge?: number;
    domain?: string;
    secure?: boolean;
    httpOnly?: boolean;
    sameSite?: boolean | 'none' | 'lax' | 'strict';
  }

  export default class Cookies {
    constructor(cookies?: string | object);
    get(name: string, options?: { doNotParse?: boolean }): string | undefined;
    getAll(options?: { doNotParse?: boolean }): Record<string, unknown>;
    set(name: string, value: unknown, options?: CookieSetOptions): void;
    remove(name: string, options?: CookieSetOptions): void;
  }
}

// react-cookie
declare module 'react-cookie' {
  interface CookieSetOptions {
    path?: string;
    expires?: Date;
    maxAge?: number;
    domain?: string;
    secure?: boolean;
    httpOnly?: boolean;
    sameSite?: boolean | 'none' | 'lax' | 'strict';
  }

  export function save(name: string, value: unknown, options?: CookieSetOptions): void;
  export function load(name: string, doNotParse?: boolean): unknown;
  export function remove(name: string, options?: CookieSetOptions): void;
}

// stacktrace-js
declare module 'stacktrace-js' {
  interface StackFrame {
    functionName?: string;
    fileName?: string;
    lineNumber?: number;
    columnNumber?: number;
  }

  interface StackTrace {
    get(options?: object): Promise<StackFrame[]>;
    fromError(error: Error, options?: object): Promise<StackFrame[]>;
  }

  const stacktrace: StackTrace;
  export default stacktrace;
}

// stackdriver-errors-js
declare module 'stackdriver-errors-js' {
  interface StartOptions {
    key: string;
    projectId: string;
    service?: string;
    version?: string;
  }

  export class StackdriverErrorReporter {
    start(options: StartOptions): void;
    report(error: Error | string, options?: object): void;
  }
}

