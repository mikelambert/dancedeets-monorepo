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

// Note: react-native-webview has its own TypeScript types

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

// Storage and persistence - redux-persist v6 API
declare module 'redux-persist' {
  import { Store, Reducer } from 'redux';

  export interface PersistConfig<S = any> {
    key: string;
    storage: Storage;
    version?: number;
    whitelist?: string[];
    blacklist?: string[];
    transforms?: Transform<any, any>[];
    throttle?: number;
    migrate?: (state: any, version: number) => Promise<any>;
    stateReconciler?: (inbound: any, original: S, reduced: S) => S;
    debug?: boolean;
    serialize?: boolean;
    writeFailHandler?: (err: Error) => void;
  }

  export interface Storage {
    getItem(key: string): Promise<string | null>;
    setItem(key: string, value: string): Promise<void>;
    removeItem(key: string): Promise<void>;
  }

  export interface Transform<HSS, ESS> {
    in: (state: HSS, key: string) => ESS;
    out: (state: ESS, key: string) => HSS;
  }

  export interface Persistor {
    pause(): void;
    persist(): void;
    purge(): Promise<void>;
    flush(): Promise<void>;
    getState(): { bootstrapped: boolean };
  }

  export function persistStore(store: Store, options?: object, callback?: () => void): Persistor;
  export function persistReducer<S>(config: PersistConfig<S>, baseReducer: Reducer<S>): Reducer<S>;
  export function createMigrate(migrations: Record<number, (state: any) => any>): (state: any, version: number) => Promise<any>;
  export function createTransform<HSS, ESS>(
    inbound: (state: HSS, key: string) => ESS,
    outbound: (state: ESS, key: string) => HSS,
    config?: { whitelist?: string[]; blacklist?: string[] }
  ): Transform<HSS, ESS>;

  export const FLUSH: string;
  export const REHYDRATE: string;
  export const PAUSE: string;
  export const PERSIST: string;
  export const PURGE: string;
  export const REGISTER: string;
}

declare module 'redux-persist/integration/react' {
  import * as React from 'react';
  import { Persistor } from 'redux-persist';

  export interface PersistGateProps {
    persistor: Persistor;
    loading?: React.ReactNode;
    onBeforeLift?: () => void | Promise<void>;
    children?: React.ReactNode;
  }

  export class PersistGate extends React.Component<PersistGateProps> {}
}

// React Navigation (older version)
declare module 'react-navigation' {
  import * as React from 'react';

  export interface NavigationParams {
    [key: string]: unknown;
  }

  export interface NavigationScreenProp<S, P = NavigationParams> {
    state: S & { params?: P };
    dispatch: (action: NavigationAction) => boolean;
    goBack: (routeKey?: string | null) => boolean;
    navigate: (routeName: string, params?: object, action?: NavigationAction) => boolean;
    setParams: (newParams: object) => boolean;
  }

  export interface NavigationRoute<P = NavigationParams> {
    key: string;
    routeName: string;
    params?: P;
  }

  export interface NavigationState {
    index: number;
    routes: NavigationRoute[];
  }

  export interface NavigationAction {
    type: string;
    routeName?: string;
    params?: object;
    action?: NavigationAction;
    key?: string;
  }

  export interface NavigationNavigateAction extends NavigationAction {
    type: 'Navigation/NAVIGATE';
    routeName: string;
    params?: object;
  }

  export type NavigationRouteConfigMap = Record<string, {
    screen: React.ComponentType<unknown>;
    navigationOptions?: object | ((options: { navigation: NavigationScreenProp<unknown> }) => object);
  }>;

  export interface StackNavigatorConfig {
    initialRouteName?: string;
    navigationOptions?: object;
    mode?: 'card' | 'modal';
    headerMode?: 'float' | 'screen' | 'none';
    cardStyle?: object;
    transitionConfig?: () => object;
  }

  export interface NavigationContainer extends React.ComponentClass<unknown> {
    router: {
      getStateForAction: (action: NavigationAction, state?: NavigationState) => NavigationState | null;
      getActionForPathAndParams: (path: string, params?: object) => NavigationAction | null;
    };
  }

  export function StackNavigator(
    routes: NavigationRouteConfigMap,
    config?: StackNavigatorConfig
  ): NavigationContainer;

  export function TabNavigator(
    routes: NavigationRouteConfigMap,
    config?: object
  ): NavigationContainer;

  export function DrawerNavigator(
    routes: NavigationRouteConfigMap,
    config?: object
  ): NavigationContainer;

  export const NavigationActions: {
    navigate: (params: { routeName: string; params?: object; action?: NavigationAction }) => NavigationNavigateAction;
    back: (params?: { key?: string }) => NavigationAction;
    reset: (params: { index: number; actions: NavigationAction[] }) => NavigationAction;
    setParams: (params: { key: string; params: object }) => NavigationAction;
    NAVIGATE: string;
    BACK: string;
    RESET: string;
    SET_PARAMS: string;
  };

  export const addNavigationHelpers: (navigation: unknown) => unknown;
  export const TabBarBottom: React.ComponentType<unknown>;
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
    // React 18 lifecycle methods
    componentDidMount?(): void;
    shouldComponentUpdate?(nextProps: P, nextState: S): boolean;
    componentDidUpdate?(prevProps: P, prevState: S): void;
    componentWillUnmount?(): void;
    // Deprecated lifecycle methods (UNSAFE_ prefix for React 18)
    UNSAFE_componentWillMount?(): void;
    UNSAFE_componentWillReceiveProps?(nextProps: P): void;
    UNSAFE_componentWillUpdate?(nextProps: P, nextState: S): void;
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

  interface Analytics {
    logEvent(name: string, params?: Record<string, unknown>): void;
    setUserProperty(name: string, value: string | null): void;
    setUserId(id: string | null): void;
    setCurrentScreen(screenName: string, screenClass?: string): void;
    setAnalyticsCollectionEnabled(enabled: boolean): void;
  }

  interface FirebaseApp {
    config(): Config;
    database(): Database;
    auth(): unknown;
    messaging(): unknown;
    analytics(): Analytics;
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

// Additional missing modules
declare module 'react-native-code-push' {
  import * as React from 'react';

  interface CodePushOptions {
    checkFrequency?: number;
    installMode?: number;
    mandatoryInstallMode?: number;
    minimumBackgroundDuration?: number;
    updateDialog?: boolean | object;
  }

  interface SyncStatus {
    UP_TO_DATE: number;
    UPDATE_INSTALLED: number;
    UPDATE_IGNORED: number;
    UNKNOWN_ERROR: number;
    SYNC_IN_PROGRESS: number;
    CHECKING_FOR_UPDATE: number;
    AWAITING_USER_ACTION: number;
    DOWNLOADING_PACKAGE: number;
    INSTALLING_UPDATE: number;
  }

  interface InstallMode {
    IMMEDIATE: number;
    ON_NEXT_RESTART: number;
    ON_NEXT_RESUME: number;
  }

  interface CheckFrequency {
    ON_APP_START: number;
    ON_APP_RESUME: number;
    MANUAL: number;
  }

  function codePush<P>(options?: CodePushOptions): (component: React.ComponentType<P>) => React.ComponentType<P>;
  function codePush<P>(component: React.ComponentType<P>): React.ComponentType<P>;

  namespace codePush {
    export const SyncStatus: SyncStatus;
    export const InstallMode: InstallMode;
    export const CheckFrequency: CheckFrequency;
    export function sync(options?: object): Promise<number>;
    export function checkForUpdate(): Promise<object | null>;
    export function getUpdateMetadata(): Promise<object | null>;
    export function notifyAppReady(): Promise<void>;
    export function restartApp(onlyIfUpdateIsPending?: boolean): void;
  }

  export = codePush;
}

declare module 'react-native-fabric' {
  export const Crashlytics: {
    crash(): void;
    log(message: string): void;
    setUserIdentifier(identifier: string): void;
    setUserName(name: string): void;
    setUserEmail(email: string): void;
    recordError(error: Error): void;
  };

  export const Answers: {
    logCustom(event: string, properties?: object): void;
    logContentView(name: string, type?: string, id?: string, properties?: object): void;
    logSignUp(method?: string, success?: boolean, properties?: object): void;
    logLogin(method?: string, success?: boolean, properties?: object): void;
    logSearch(query: string, properties?: object): void;
    logShare(method?: string, contentName?: string, contentType?: string, contentId?: string, properties?: object): void;
    logPurchase(price?: number, currency?: string, success?: boolean, itemName?: string, itemType?: string, itemId?: string, properties?: object): void;
  };
}

declare module 'react-native-gifted-form' {
  import * as React from 'react';

  interface GiftedFormProps {
    formName?: string;
    openModal?: (route: object) => void;
    clearOnClose?: boolean;
    defaults?: object;
    validators?: object;
    children?: React.ReactNode;
  }

  export class GiftedForm extends React.Component<GiftedFormProps> {
    static TextInputWidget: React.ComponentType<any>;
    static SwitchWidget: React.ComponentType<any>;
    static SelectWidget: React.ComponentType<any>;
    static SelectCountryWidget: React.ComponentType<any>;
    static DatePickerWidget: React.ComponentType<any>;
    static ModalWidget: React.ComponentType<any>;
    static GroupWidget: React.ComponentType<any>;
    static RowWidget: React.ComponentType<any>;
    static RowValueWidget: React.ComponentType<any>;
    static SeparatorWidget: React.ComponentType<any>;
    static NoticeWidget: React.ComponentType<any>;
    static SubmitWidget: React.ComponentType<any>;
    static LoadingWidget: React.ComponentType<any>;
    static OptionWidget: React.ComponentType<any>;
    static HiddenWidget: React.ComponentType<any>;
  }

  export class GiftedFormManager {
    static getValue(formName: string, key: string): unknown;
    static getValues(formName: string): object;
    static setValue(formName: string, key: string, value: unknown): void;
    static reset(formName: string): void;
    static validate(formName: string): string[];
  }
}

declare module 'react-native-processinfo' {
  interface ProcessInfo {
    environment: Record<string, string>;
    arguments: string[];
  }

  const processInfo: ProcessInfo;
  export default processInfo;
}

declare module 'react-native-tab-view/src/TabViewTypeDefinitions' {
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

  export interface Scene<T extends Route> {
    route: T;
    index: number;
    focused: boolean;
  }
}

declare module 'react-native-vector-icons/FontAwesome' {
  import * as React from 'react';
  import { TextProps } from 'react-native';

  interface IconProps extends TextProps {
    name: string;
    size?: number;
    color?: string;
  }

  export default class FontAwesome extends React.Component<IconProps> {
    static getImageSource(name: string, size?: number, color?: string): Promise<unknown>;
    static loadFont(): Promise<void>;
  }
}

declare module 'react-native-vector-icons/Ionicons' {
  import * as React from 'react';
  import { TextProps } from 'react-native';

  interface IconProps extends TextProps {
    name: string;
    size?: number;
    color?: string;
  }

  export default class Ionicons extends React.Component<IconProps> {
    static getImageSource(name: string, size?: number, color?: string): Promise<unknown>;
    static loadFont(): Promise<void>;
  }
}

declare module 'react-native/Libraries/StyleSheet/normalizeColor' {
  function normalizeColor(color: string | number): number | null;
  export = normalizeColor;
}

declare module 'react-navigation/src/TypeDefinition' {
  export * from 'react-navigation';
}

declare module 'react-navigation/src/views/TouchableItem' {
  import * as React from 'react';
  import { TouchableOpacityProps } from 'react-native';

  export default class TouchableItem extends React.Component<TouchableOpacityProps> {}
}

// Note: react-redux/lib/utils/storeShape was removed in react-redux v8.
// Use the connect HOC or useSelector/useDispatch hooks instead of legacy context.

declare module 'react-tabs' {
  import * as React from 'react';

  interface TabProps {
    className?: string;
    disabled?: boolean;
    disabledClassName?: string;
    selectedClassName?: string;
    children?: React.ReactNode;
  }

  interface TabListProps {
    className?: string;
    children?: React.ReactNode;
  }

  interface TabPanelProps {
    className?: string;
    forceRender?: boolean;
    selectedClassName?: string;
    children?: React.ReactNode;
  }

  interface TabsProps {
    className?: string;
    defaultFocus?: boolean;
    defaultIndex?: number;
    disabledTabClassName?: string;
    domRef?: (node: HTMLElement) => void;
    forceRenderTabPanel?: boolean;
    onSelect?: (index: number, lastIndex: number, event: Event) => boolean | void;
    selectedIndex?: number;
    selectedTabClassName?: string;
    selectedTabPanelClassName?: string;
    children?: React.ReactNode;
  }

  export class Tab extends React.Component<TabProps> {}
  export class TabList extends React.Component<TabListProps> {}
  export class TabPanel extends React.Component<TabPanelProps> {}
  export class Tabs extends React.Component<TabsProps> {}
  export function resetIdCounter(): void;
}

declare module 'react-waypoint' {
  import * as React from 'react';

  interface WaypointProps {
    onEnter?: (args: { previousPosition: string; currentPosition: string; event: Event }) => void;
    onLeave?: (args: { previousPosition: string; currentPosition: string; event: Event }) => void;
    onPositionChange?: (args: { previousPosition: string; currentPosition: string; event: Event }) => void;
    fireOnRapidScroll?: boolean;
    scrollableAncestor?: unknown;
    horizontal?: boolean;
    topOffset?: string | number;
    bottomOffset?: string | number;
    children?: React.ReactNode;
  }

  export default class Waypoint extends React.Component<WaypointProps> {}
}

declare module 'style-equal' {
  function styleEqual(a: object, b: object): boolean;
  export = styleEqual;
}

declare module 'react-dates' {
  import * as React from 'react';
  import * as Moment from 'moment';

  interface DateRangePickerProps {
    startDate: Moment.Moment | null;
    startDateId: string;
    endDate: Moment.Moment | null;
    endDateId: string;
    onDatesChange: (arg: { startDate: Moment.Moment | null; endDate: Moment.Moment | null }) => void;
    focusedInput: 'startDate' | 'endDate' | null;
    onFocusChange: (focusedInput: 'startDate' | 'endDate' | null) => void;
    onClose?: (arg: { startDate: Moment.Moment | null; endDate: Moment.Moment | null }) => void;
    minimumNights?: number;
    isOutsideRange?: (day: Moment.Moment) => boolean;
    displayFormat?: string | (() => string);
    monthFormat?: string;
    showClearDates?: boolean;
    disabled?: boolean;
    required?: boolean;
    readOnly?: boolean;
    screenReaderInputMessage?: string;
    showDefaultInputIcon?: boolean;
    customInputIcon?: React.ReactNode;
    customArrowIcon?: React.ReactNode;
    noBorder?: boolean;
    block?: boolean;
    small?: boolean;
    regular?: boolean;
    numberOfMonths?: number;
    orientation?: 'horizontal' | 'vertical';
    anchorDirection?: 'left' | 'right';
    horizontalMargin?: number;
    withPortal?: boolean;
    withFullScreenPortal?: boolean;
    initialVisibleMonth?: () => Moment.Moment;
    firstDayOfWeek?: 0 | 1 | 2 | 3 | 4 | 5 | 6;
    hideKeyboardShortcutsPanel?: boolean;
    daySize?: number;
    keepOpenOnDateSelect?: boolean;
    reopenPickerOnClearDates?: boolean;
    renderCalendarInfo?: () => React.ReactNode;
    navPrev?: React.ReactNode;
    navNext?: React.ReactNode;
    renderMonthText?: (month: Moment.Moment) => React.ReactNode;
    renderDayContents?: (day: Moment.Moment) => React.ReactNode;
    enableOutsideDays?: boolean;
    isDayBlocked?: (day: Moment.Moment) => boolean;
    isDayHighlighted?: (day: Moment.Moment) => boolean;
    phrases?: object;
  }

  export class DateRangePicker extends React.Component<DateRangePickerProps> {}

  interface SingleDatePickerProps {
    date: Moment.Moment | null;
    onDateChange: (date: Moment.Moment | null) => void;
    focused: boolean;
    onFocusChange: (arg: { focused: boolean }) => void;
    id: string;
    placeholder?: string;
    disabled?: boolean;
    required?: boolean;
    readOnly?: boolean;
    displayFormat?: string | (() => string);
    monthFormat?: string;
    showClearDate?: boolean;
    screenReaderInputMessage?: string;
    showDefaultInputIcon?: boolean;
    customInputIcon?: React.ReactNode;
    noBorder?: boolean;
    block?: boolean;
    small?: boolean;
    regular?: boolean;
    numberOfMonths?: number;
    orientation?: 'horizontal' | 'vertical';
    anchorDirection?: 'left' | 'right';
    horizontalMargin?: number;
    withPortal?: boolean;
    withFullScreenPortal?: boolean;
    initialVisibleMonth?: () => Moment.Moment;
    firstDayOfWeek?: 0 | 1 | 2 | 3 | 4 | 5 | 6;
    hideKeyboardShortcutsPanel?: boolean;
    daySize?: number;
    keepOpenOnDateSelect?: boolean;
    renderCalendarInfo?: () => React.ReactNode;
    navPrev?: React.ReactNode;
    navNext?: React.ReactNode;
    onPrevMonthClick?: (newCurrentMonth: Moment.Moment) => void;
    onNextMonthClick?: (newCurrentMonth: Moment.Moment) => void;
    onClose?: (arg: { date: Moment.Moment | null }) => void;
    renderMonthText?: (month: Moment.Moment) => React.ReactNode;
    renderDayContents?: (day: Moment.Moment) => React.ReactNode;
    enableOutsideDays?: boolean;
    isDayBlocked?: (day: Moment.Moment) => boolean;
    isOutsideRange?: (day: Moment.Moment) => boolean;
    isDayHighlighted?: (day: Moment.Moment) => boolean;
    phrases?: object;
  }

  export class SingleDatePicker extends React.Component<SingleDatePickerProps> {}

  interface DayPickerRangeControllerProps {
    startDate: Moment.Moment | null;
    endDate: Moment.Moment | null;
    onDatesChange: (arg: { startDate: Moment.Moment | null; endDate: Moment.Moment | null }) => void;
    focusedInput: 'startDate' | 'endDate' | null;
    onFocusChange: (focusedInput: 'startDate' | 'endDate' | null) => void;
    minimumNights?: number;
    isOutsideRange?: (day: Moment.Moment) => boolean;
    isDayBlocked?: (day: Moment.Moment) => boolean;
    isDayHighlighted?: (day: Moment.Moment) => boolean;
    initialVisibleMonth?: () => Moment.Moment;
    numberOfMonths?: number;
    enableOutsideDays?: boolean;
    withPortal?: boolean;
    hideKeyboardShortcutsPanel?: boolean;
    daySize?: number;
    keepOpenOnDateSelect?: boolean;
    renderDayContents?: (day: Moment.Moment) => React.ReactNode;
    phrases?: object;
  }

  export class DayPickerRangeController extends React.Component<DayPickerRangeControllerProps> {}

  export const START_DATE: 'startDate';
  export const END_DATE: 'endDate';
  export const HORIZONTAL_ORIENTATION: 'horizontal';
  export const VERTICAL_ORIENTATION: 'vertical';
  export const ANCHOR_LEFT: 'left';
  export const ANCHOR_RIGHT: 'right';
}

declare module 'react-format-text' {
  import * as React from 'react';

  interface FormatTextProps {
    children: string;
    allowedFormats?: string[];
  }

  export default class FormatText extends React.Component<FormatTextProps> {}
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

  // Note: intlShape was removed in react-intl v6. Use injectIntl or useIntl hook instead.

  // react-intl v6 renamed InjectedIntlProps to WrappedComponentProps
  export interface WrappedComponentProps {
    intl: IntlShape;
  }

  // Backward compatibility alias
  export type InjectedIntlProps = WrappedComponentProps;

  export function injectIntl<P extends WrappedComponentProps>(
    component: React.ComponentType<P>
  ): React.ComponentType<Omit<P, keyof WrappedComponentProps>>;

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

  // Hook for functional components
  export function useIntl(): IntlShape;

  // For creating intl instances outside of React
  export interface IntlCache {}
  export function createIntlCache(): IntlCache;
  export function createIntl(
    config: { locale: string; messages: Record<string, string>; defaultLocale?: string },
    cache?: IntlCache
  ): IntlShape;
}
