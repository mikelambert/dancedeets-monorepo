/**
 * Type declarations for packages without @types.
 */

// React Native ecosystem packages
declare module 'react-native-autolink' {
  import * as React from 'react';
  import { TextProps } from 'react-native';

  interface AutolinkProps extends TextProps {
    text: string;
    email?: boolean;
    hashtag?: boolean | string;
    mention?: boolean | string;
    phone?: boolean | string;
    url?: boolean;
    linkStyle?: object;
    onPress?: (url: string, match: unknown) => void;
  }

  export default class Autolink extends React.Component<AutolinkProps> {}
}

declare module 'react-native-carousel' {
  import * as React from 'react';
  import { ViewProps } from 'react-native';

  interface CarouselProps extends ViewProps {
    delay?: number;
    animate?: boolean;
    loop?: boolean;
    inactiveIndicatorColor?: string;
    indicatorColor?: string;
    indicatorOffset?: number;
    indicatorSize?: number;
    indicatorSpace?: number;
    onPageChange?: (pageNumber: number) => void;
    children?: React.ReactNode;
  }

  export default class Carousel extends React.Component<CarouselProps> {}
}

declare module 'react-native-collapsible' {
  import * as React from 'react';

  interface CollapsibleProps {
    collapsed?: boolean;
    align?: 'top' | 'center' | 'bottom';
    duration?: number;
    easing?: string | ((t: number) => number);
    children?: React.ReactNode;
  }

  export default class Collapsible extends React.Component<CollapsibleProps> {}
}

declare module 'react-native-linear-gradient' {
  import * as React from 'react';
  import { ViewProps } from 'react-native';

  interface LinearGradientProps extends ViewProps {
    colors: string[];
    start?: { x: number; y: number };
    end?: { x: number; y: number };
    locations?: number[];
    children?: React.ReactNode;
  }

  export default class LinearGradient extends React.Component<LinearGradientProps> {}
}

declare module 'react-native-youtube' {
  import * as React from 'react';
  import { ViewProps } from 'react-native';

  interface YouTubeProps extends ViewProps {
    apiKey?: string;
    videoId?: string;
    playlistId?: string;
    play?: boolean;
    loop?: boolean;
    fullscreen?: boolean;
    controls?: number;
    showInfo?: boolean;
    modestBranding?: boolean;
    origin?: string;
    rel?: boolean;
    onReady?: (e: unknown) => void;
    onChangeState?: (e: { state: string }) => void;
    onChangeQuality?: (e: unknown) => void;
    onChangeFullscreen?: (e: { isFullscreen: boolean }) => void;
    onError?: (e: { error: string }) => void;
    onProgress?: (e: { currentTime: number; duration: number }) => void;
  }

  export default class YouTube extends React.Component<YouTubeProps> {}
}

declare module 'react-native-video' {
  import * as React from 'react';
  import { ViewProps } from 'react-native';

  interface VideoProps extends ViewProps {
    source: { uri: string } | number;
    paused?: boolean;
    muted?: boolean;
    volume?: number;
    rate?: number;
    repeat?: boolean;
    resizeMode?: 'contain' | 'cover' | 'stretch';
    controls?: boolean;
    onLoad?: (data: unknown) => void;
    onLoadStart?: () => void;
    onProgress?: (data: { currentTime: number; playableDuration: number }) => void;
    onEnd?: () => void;
    onError?: (error: unknown) => void;
    onBuffer?: (data: { isBuffering: boolean }) => void;
  }

  export default class Video extends React.Component<VideoProps> {}
}

declare module 'react-native-video-controls' {
  import * as React from 'react';
  import { VideoProps } from 'react-native-video';

  interface VideoControlsProps extends VideoProps {
    toggleResizeModeOnFullscreen?: boolean;
    controlTimeout?: number;
    videoStyle?: object;
    navigator?: unknown;
    seekColor?: string;
    tapAnywhereToPause?: boolean;
    onEnterFullscreen?: () => void;
    onExitFullscreen?: () => void;
    onPause?: () => void;
    onPlay?: () => void;
  }

  export default class VideoPlayer extends React.Component<VideoControlsProps> {}
}

declare module 'react-native-tab-view' {
  import * as React from 'react';

  export interface Route {
    key: string;
    title?: string;
    icon?: string;
    [key: string]: unknown;
  }

  export interface NavigationState<T extends Route> {
    index: number;
    routes: T[];
  }

  export interface SceneRendererProps {
    navigationState: NavigationState<Route>;
    position: unknown;
    jumpToIndex: (index: number) => void;
    getLastPosition: () => number;
    subscribe: (type: string, callback: unknown) => { remove: () => void };
  }

  export interface TabViewProps<T extends Route> {
    navigationState: NavigationState<T>;
    renderScene: (props: SceneRendererProps & { route: T }) => React.ReactNode;
    renderHeader?: (props: SceneRendererProps) => React.ReactNode;
    renderFooter?: (props: SceneRendererProps) => React.ReactNode;
    renderTabBar?: (props: SceneRendererProps) => React.ReactNode;
    onRequestChangeTab?: (index: number) => void;
    onChangePosition?: (position: number) => void;
    lazy?: boolean;
    initialLayout?: { width: number; height: number };
    style?: object;
  }

  export class TabViewAnimated<T extends Route> extends React.Component<TabViewProps<T>> {}
  export class TabViewPagerPan<T extends Route> extends React.Component<unknown> {}
  export class TabViewPagerScroll<T extends Route> extends React.Component<unknown> {}
  export class TabBar<T extends Route> extends React.Component<unknown> {}
}

declare module 'react-native-fit-image' {
  import * as React from 'react';
  import { ImageProps } from 'react-native';

  interface FitImageProps extends ImageProps {
    indicator?: boolean;
    indicatorColor?: string;
    indicatorSize?: 'small' | 'large' | number;
    originalWidth?: number;
    originalHeight?: number;
  }

  export default class FitImage extends React.Component<FitImageProps> {}
}

declare module 'react-native-photo-view' {
  import * as React from 'react';
  import { ImageSourcePropType, ViewProps } from 'react-native';

  interface PhotoViewProps extends ViewProps {
    source: ImageSourcePropType;
    loadingIndicatorSource?: ImageSourcePropType;
    fadeDuration?: number;
    minimumZoomScale?: number;
    maximumZoomScale?: number;
    showsHorizontalScrollIndicator?: boolean;
    showsVerticalScrollIndicator?: boolean;
    scale?: number;
    onLoadStart?: () => void;
    onLoad?: () => void;
    onLoadEnd?: () => void;
    onProgress?: (loaded: number, total: number) => void;
    onTap?: (point: { x: number; y: number }) => void;
    onViewTap?: (point: { x: number; y: number }) => void;
    onScale?: (scale: number) => void;
  }

  export default class PhotoView extends React.Component<PhotoViewProps> {}
}

declare module 'react-native-wkwebview-reborn' {
  import * as React from 'react';
  import { WebViewProps } from 'react-native';

  export default class WKWebView extends React.Component<WebViewProps> {}
}

// Utility packages
declare module 'json-prune' {
  function prune(value: unknown, options?: object): string;
  export = prune;
}

declare module 'emoji-flags' {
  interface Country {
    code: string;
    name: string;
    emoji: string;
    unicode: string;
  }
  const flags: {
    countryCode: (code: string) => Country | undefined;
    data: Country[];
  };
  export = flags;
}

declare module 'geolib' {
  interface Point {
    latitude: number;
    longitude: number;
  }

  export function getDistance(start: Point, end: Point, accuracy?: number): number;
  export function getDistanceSimple(start: Point, end: Point, accuracy?: number): number;
  export function orderByDistance(point: Point, coords: Point[]): Point[];
  export function findNearest(point: Point, coords: Point[]): Point;
  export function getCenter(coords: Point[]): Point | false;
  export function getCenterOfBounds(coords: Point[]): Point | false;
  export function getBounds(coords: Point[]): { minLat: number; maxLat: number; minLng: number; maxLng: number };
  export function isPointInCircle(point: Point, center: Point, radius: number): boolean;
  export function isPointInside(point: Point, polygon: Point[]): boolean;
}

// React Native plugins
declare module 'react-native-back-android' {
  export function exitApp(): void;
  export function addEventListener(event: string, handler: () => boolean): void;
  export function removeEventListener(event: string, handler: () => boolean): void;
}

declare module 'react-native-device-info' {
  export function getVersion(): string;
  export function getBuildNumber(): string;
  export function getDeviceId(): string;
  export function getSystemVersion(): string;
  export function getModel(): string;
  export function getBrand(): string;
  export function getDeviceName(): Promise<string>;
  export function isEmulator(): Promise<boolean>;
  export function getUniqueId(): string;
}

declare module 'react-native-locale' {
  export function getLocale(): string;
  export function getPreferredLocales(): string[];
}

declare module 'react-native-mixpanel' {
  export function sharedInstanceWithToken(token: string): void;
  export function track(event: string, properties?: object): void;
  export function identify(id: string): void;
  export function set(properties: object): void;
  export function setOnce(properties: object): void;
}

declare module 'react-native-permissions' {
  type PermissionType = 'location' | 'camera' | 'microphone' | 'photo' | 'contacts' | 'event' | 'bluetooth' | 'reminder' | 'notification' | 'backgroundRefresh' | 'speechRecognition' | 'mediaLibrary' | 'motion';
  type PermissionStatus = 'authorized' | 'denied' | 'restricted' | 'undetermined';

  export function check(type: PermissionType): Promise<PermissionStatus>;
  export function request(type: PermissionType): Promise<PermissionStatus>;
  export function checkMultiple(types: PermissionType[]): Promise<Record<PermissionType, PermissionStatus>>;
  export function openSettings(): Promise<void>;
}

declare module 'react-native-share' {
  interface ShareOptions {
    title?: string;
    message?: string;
    url?: string;
    subject?: string;
    failOnCancel?: boolean;
  }

  export default {
    open(options: ShareOptions): Promise<{ app: string }>;
  };
}

declare module 'react-native-mail' {
  interface MailOptions {
    subject?: string;
    recipients?: string[];
    ccRecipients?: string[];
    bccRecipients?: string[];
    body?: string;
    isHTML?: boolean;
    attachment?: {
      path: string;
      type: string;
      name: string;
    };
  }

  export default {
    mail(options: MailOptions, callback: (error: unknown, event: unknown) => void): void;
  };
}

declare module 'react-native-geocoder' {
  interface Position {
    lat: number;
    lng: number;
  }

  interface GeocodingObject {
    position: Position;
    formattedAddress: string;
    feature: string | null;
    streetNumber: string | null;
    streetName: string | null;
    postalCode: string | null;
    locality: string | null;
    country: string;
    countryCode: string;
    adminArea: string | null;
    subAdminArea: string | null;
    subLocality: string | null;
  }

  interface Geocoder {
    geocodeAddress(address: string): Promise<GeocodingObject[]>;
    geocodePosition(position: Position): Promise<GeocodingObject[]>;
    fallbackToGoogle(key: string): void;
  }

  const geocoder: Geocoder;
  export default geocoder;
}

declare module 'react-native-send-intent' {
  export function openCalendar(): void;
  export function openMaps(address: string): void;
  export function openMapsWithRoute(address: string, mode: string): void;
  export function sendPhoneDial(phoneNumber: string): void;
  export function sendSms(phoneNumber: string, body: string): void;
  export function sendMail(email: string, options: { subject?: string; body?: string }): void;
  export function openApp(packageName: string, extras?: object): Promise<boolean>;
  export function openAppWithData(packageName: string, dataUri: string): Promise<boolean>;
}

declare module 'react-native-version-number' {
  export const appVersion: string;
  export const buildVersion: string;
  export const bundleIdentifier: string;
}

// Storage and persistence
declare module 'redux-persist' {
  import { Store } from 'redux';

  export interface PersistConfig {
    key?: string;
    storage?: unknown;
    whitelist?: string[];
    blacklist?: string[];
    transforms?: unknown[];
    debounce?: number;
  }

  export function persistStore(store: Store, config?: PersistConfig, callback?: () => void): unknown;
  export function autoRehydrate(config?: { log?: boolean }): unknown;
}

// React Navigation (older version)
declare module 'react-navigation' {
  import * as React from 'react';

  export interface NavigationScreenProp<S> {
    state: S;
    dispatch: (action: unknown) => boolean;
    goBack: (routeKey?: string | null) => boolean;
    navigate: (routeName: string, params?: object, action?: unknown) => boolean;
    setParams: (newParams: object) => boolean;
  }

  export interface NavigationRoute {
    key: string;
    routeName: string;
    params?: object;
  }

  export interface NavigationState {
    index: number;
    routes: NavigationRoute[];
  }

  export type NavigationContainer = React.ComponentType<unknown>;

  export function StackNavigator(
    routes: Record<string, { screen: React.ComponentType<unknown>; navigationOptions?: object }>,
    config?: object
  ): NavigationContainer;

  export function TabNavigator(
    routes: Record<string, { screen: React.ComponentType<unknown>; navigationOptions?: object }>,
    config?: object
  ): NavigationContainer;

  export function DrawerNavigator(
    routes: Record<string, { screen: React.ComponentType<unknown>; navigationOptions?: object }>,
    config?: object
  ): NavigationContainer;

  export function NavigationActions(): unknown;
  export const addNavigationHelpers: (navigation: unknown) => unknown;
}

// Create React Class (legacy)
declare module 'create-react-class' {
  import * as React from 'react';

  interface ComponentSpec<P, S> {
    render(): React.ReactNode;
    getInitialState?(): S;
    getDefaultProps?(): P;
    propTypes?: object;
    mixins?: unknown[];
    statics?: object;
    displayName?: string;
    componentWillMount?(): void;
    componentDidMount?(): void;
    componentWillReceiveProps?(nextProps: P): void;
    shouldComponentUpdate?(nextProps: P, nextState: S): boolean;
    componentWillUpdate?(nextProps: P, nextState: S): void;
    componentDidUpdate?(prevProps: P, prevState: S): void;
    componentWillUnmount?(): void;
    [key: string]: unknown;
  }

  function createReactClass<P, S>(spec: ComponentSpec<P, S>): React.ComponentClass<P>;
  export = createReactClass;
}

// Firebase
declare module 'react-native-firebase' {
  interface ConfigResult {
    val(): string;
  }

  interface Config {
    enableDeveloperMode(): void;
    fetch(): Promise<void>;
    activateFetched(): Promise<void>;
    getValue(key: string): Promise<ConfigResult | null>;
  }

  interface DataSnapshot {
    val(): unknown;
    key: string | null;
    exists(): boolean;
    forEach(action: (snapshot: DataSnapshot) => boolean | void): boolean;
    child(path: string): DataSnapshot;
  }

  interface Reference {
    on(eventType: string, callback: (snapshot: DataSnapshot) => void): void;
    off(eventType?: string, callback?: (snapshot: DataSnapshot) => void): void;
    set(value: unknown): Promise<void>;
    update(values: object): Promise<void>;
    remove(): Promise<void>;
    push(value?: unknown): Reference;
    child(path: string): Reference;
  }

  interface Database {
    ref(path?: string): Reference;
  }

  interface FirebaseApp {
    config(): Config;
    database(): Database;
    auth(): unknown;
    messaging(): unknown;
    analytics(): unknown;
  }

  const firebase: FirebaseApp;
  export default firebase;
}

// Error tracking
declare module 'react-native-trackjs' {
  interface TrackJSConfig {
    token: string;
    application?: string;
  }

  export function init(config: TrackJSConfig): void;
  export function track(error: Error): void;
}

declare module 'react-native-fabric-crashlytics' {
  export function init(): void;
  export function crash(): void;
  export function log(message: string): void;
  export function setUserIdentifier(identifier: string): void;
  export function setUserName(name: string): void;
  export function setUserEmail(email: string): void;
  export function recordError(error: Error): void;
}

declare module 'react-native-sentry' {
  interface SentryConfig {
    deactivateStacktraceMerging?: boolean;
  }

  interface SentryConfigurable {
    install(config?: SentryConfig): void;
  }

  export const Sentry: {
    config(dsn: string): SentryConfigurable;
    captureException(error: Error): void;
    captureMessage(message: string): void;
    setUserContext(user: object): void;
  };
}

// Calendar
declare module 'react-native-calendar-events' {
  interface CalendarEvent {
    id: string;
    title: string;
    startDate: string;
    endDate: string;
    location?: string;
    notes?: string;
    url?: string;
  }

  interface CalendarEventWritable {
    title: string;
    startDate: string;
    endDate: string;
    location?: string;
    notes?: string;
    url?: string;
    calendarId?: string;
  }

  export function authorizationStatus(): Promise<string>;
  export function authorizeEventStore(): Promise<string>;
  export function findEventById(id: string): Promise<CalendarEvent | null>;
  export function fetchAllEvents(startDate: string, endDate: string): Promise<CalendarEvent[]>;
  export function saveEvent(title: string, details: CalendarEventWritable): Promise<string>;
  export function removeEvent(id: string): Promise<boolean>;
}

// Google API
declare module 'react-native-google-api-availability' {
  export function checkGooglePlayServices(): Promise<string>;
  export function promptGooglePlayUpdate(showDialog?: boolean): Promise<number>;
}

// Segmented control
declare module 'react-native-segmented-android' {
  import * as React from 'react';

  interface SegmentedControlProps {
    values: string[];
    selectedIndex?: number;
    onChange?: (event: { nativeEvent: { selectedSegmentIndex: number } }) => void;
    tintColor?: string;
    enabled?: boolean;
    style?: object;
  }

  export default class SegmentedControl extends React.Component<SegmentedControlProps> {}
}

// Push notifications
declare module 'react-native-push-notification' {
  interface PushNotificationConfig {
    onRegister?: (token: { token: string }) => void;
    onNotification?: (notification: object) => void;
    onAction?: (notification: object) => void;
    onRegistrationError?: (error: Error) => void;
    permissions?: {
      alert?: boolean;
      badge?: boolean;
      sound?: boolean;
    };
    popInitialNotification?: boolean;
    requestPermissions?: boolean;
    senderID?: string;
  }

  interface LocalNotification {
    id?: string;
    title?: string;
    message: string;
    playSound?: boolean;
    soundName?: string;
    number?: number;
    repeatType?: 'week' | 'day' | 'hour' | 'minute' | 'time';
    actions?: string[];
    category?: string;
    userInfo?: object;
  }

  export function configure(config: PushNotificationConfig): void;
  export function localNotification(notification: LocalNotification): void;
  export function localNotificationSchedule(notification: LocalNotification & { date: Date }): void;
  export function cancelLocalNotifications(userInfo: object): void;
  export function cancelAllLocalNotifications(): void;
  export function requestPermissions(): void;
  export function abandonPermissions(): void;
  export function checkPermissions(callback: (permissions: object) => void): void;
  export function getInitialNotification(): Promise<object | null>;
}

// URL parsing (for React Native)
declare module 'url' {
  interface UrlObject {
    protocol?: string;
    slashes?: boolean;
    auth?: string;
    host?: string;
    port?: string;
    hostname?: string;
    hash?: string;
    search?: string;
    query?: Record<string, string | undefined>;
    pathname?: string;
    path?: string;
    href?: string;
  }

  export class Url {
    parse(urlStr: string, parseQueryString?: boolean): UrlObject;
    format(urlObj: UrlObject): string;
    resolve(from: string, to: string): string;
  }
}

// React Native locale (extended)
declare module 'react-native-locale' {
  interface LocaleConstants {
    localeIdentifier: string;
    decimalSeparator: string;
    groupingSeparator: string;
    currencySymbol: string;
    currencyCode: string;
  }

  const Locale: {
    constants(): LocaleConstants;
    decimalStyle(value: number): string;
    percentStyle(value: number): string;
    currencyStyle(value: number): string;
  };

  export default Locale;
}

// Global declarations
declare const __DEV__: boolean;

// Facebook SDK
declare module 'react-native-fbsdk' {
  export interface AccessToken {
    accessToken: string;
    applicationID: string;
    userID: string;
    permissions: string[];
    declinedPermissions: string[];
    expirationTime: number;
    lastRefreshTime: number;
  }

  export const AccessToken: {
    getCurrentAccessToken(): Promise<AccessToken | null>;
    refreshCurrentAccessTokenAsync(): Promise<AccessToken>;
    setCurrentAccessToken(token: AccessToken): void;
  };

  export const LoginManager: {
    logInWithReadPermissions(permissions: string[]): Promise<{ isCancelled: boolean; grantedPermissions?: string[] }>;
    logInWithPublishPermissions(permissions: string[]): Promise<{ isCancelled: boolean; grantedPermissions?: string[] }>;
    logOut(): void;
    getLoginBehavior(): Promise<string>;
    setLoginBehavior(behavior: string): void;
  };

  export interface GraphRequestConfig {
    httpMethod?: string;
    version?: string;
    parameters?: Record<string, { string: string }>;
    accessToken?: string;
  }

  export class GraphRequest {
    constructor(graphPath: string, config?: GraphRequestConfig, callback?: (error: unknown, result: unknown) => void);
  }

  export class GraphRequestManager {
    addRequest(request: GraphRequest): GraphRequestManager;
    start(): void;
  }

  export interface ShareContent {
    contentType: 'link' | 'photo' | 'video';
    contentUrl?: string;
    contentDescription?: string;
    contentTitle?: string;
    imageUrl?: string;
    photos?: Array<{ imageUrl: string }>;
  }

  export const ShareDialog: {
    canShow(content: ShareContent): Promise<boolean>;
    show(content: ShareContent): Promise<{ postId?: string }>;
    setMode(mode: string): void;
  };
}

// React Intl
declare module 'react-intl' {
  import * as React from 'react';

  export interface MessageDescriptor {
    id: string;
    defaultMessage?: string;
    description?: string;
  }

  export interface IntlShape {
    formatMessage(descriptor: MessageDescriptor, values?: Record<string, unknown>): string;
    formatNumber(value: number, options?: Intl.NumberFormatOptions): string;
    formatDate(value: Date | number, options?: Intl.DateTimeFormatOptions): string;
    formatTime(value: Date | number, options?: Intl.DateTimeFormatOptions): string;
    formatRelative(value: Date | number): string;
    locale: string;
    messages: Record<string, string>;
  }

  export const intlShape: IntlShape;

  export interface InjectedIntlProps {
    intl: IntlShape;
  }

  export function injectIntl<P extends InjectedIntlProps>(
    component: React.ComponentType<P>
  ): React.ComponentType<Omit<P, keyof InjectedIntlProps>>;

  export function defineMessages<T extends Record<string, MessageDescriptor>>(messages: T): T;

  export interface IntlProviderProps {
    locale: string;
    messages?: Record<string, string>;
    defaultLocale?: string;
    children: React.ReactNode;
  }

  export class IntlProvider extends React.Component<IntlProviderProps> {}

  export interface FormattedMessageProps extends MessageDescriptor {
    values?: Record<string, unknown>;
    tagName?: string;
  }

  export class FormattedMessage extends React.Component<FormattedMessageProps> {}
  export class FormattedNumber extends React.Component<{ value: number; style?: string }> {}
  export class FormattedDate extends React.Component<{ value: Date | number }> {}
}
