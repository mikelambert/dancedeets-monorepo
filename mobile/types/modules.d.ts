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
    hidden?: boolean;
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
  import { Animated, PanResponderInstance } from 'react-native';

  interface VideoControlsProps {
    source: { uri: string } | number;
    paused?: boolean;
    muted?: boolean;
    volume?: number;
    rate?: number;
    repeat?: boolean;
    loop?: boolean;
    resizeMode?: 'contain' | 'cover' | 'stretch';
    controls?: boolean;
    onLoad?: (data: unknown) => void;
    onLoadStart?: () => void;
    onProgress?: (data: { currentTime: number; playableDuration: number }) => void;
    onEnd?: () => void;
    onError?: (error: unknown) => void;
    onBuffer?: (data: { isBuffering: boolean }) => void;
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
    style?: object;
    ignoreSilentSwitch?: string;
  }

  interface VideoPlayerState {
    paused: boolean;
    seeking: boolean;
    loading: boolean;
    duration: number;
    currentTime: number;
    seekerOffset: number;
    seekerFillWidth: number;
    seekerPosition: number;
    showControls: boolean;
  }

  export default class VideoPlayer extends React.Component<VideoControlsProps, VideoPlayerState> {
    // Internal objects used when extending
    events: {
      onScreenPress: () => void;
      onEnd: () => void;
    };
    animations: {
      bottomControl: {
        opacity: Animated.Value;
        marginBottom: Animated.Value;
      };
      topControl: {
        opacity: Animated.Value;
        marginTop: Animated.Value;
      };
    };
    player: {
      seekPanResponder: PanResponderInstance;
      seekerWidth: number;
    };
    methods: {
      togglePlayPause: () => void;
      toggleTimer: () => void;
      toggleControls: () => void;
    };

    // Methods available for override
    setControlTimeout(): void;
    hideControlAnimation(): void;
    showControlAnimation(): void;
    initSeekPanResponder(): void;
    setSeekerPosition(position: number): void;
    calculateTimeFromSeekerPosition(): number;
    seekTo(time: number): void;
    calculateTime(): string;
    renderControl(
      children: React.ReactNode,
      callback?: () => void,
      style?: object
    ): React.ReactElement;
    renderTopControls(): React.ReactNode;
    renderBottomControls(): React.ReactNode;
    renderPlayPause(): React.ReactNode;
    renderSeekbar(): React.ReactNode;
    renderTimer(): React.ReactNode;
  }
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
    androidScaleType?: 'center' | 'centerCrop' | 'centerInside' | 'fitCenter' | 'fitStart' | 'fitEnd' | 'fitXY';
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
  import * as React from 'react';

  export function exitApp(): void;
  export function addEventListener(event: string, handler: () => boolean): void;
  export function removeEventListener(event: string, handler: () => boolean): void;

  // HOC that wraps a component with back button handling
  function backAndroid<P>(WrappedComponent: React.ComponentType<P>): React.ComponentType<P>;
  export default backAndroid;
}

// react-native-device-info v10+ API
declare module 'react-native-device-info' {
  // Sync methods (available immediately)
  export function getVersionSync(): string;
  export function getBuildNumberSync(): string;
  export function getDeviceIdSync(): string;
  export function getSystemVersionSync(): string;
  export function getModelSync(): string;
  export function getBrandSync(): string;
  export function getUniqueIdSync(): string;

  // Async methods
  export function getVersion(): Promise<string>;
  export function getBuildNumber(): Promise<string>;
  export function getDeviceId(): Promise<string>;
  export function getSystemVersion(): Promise<string>;
  export function getModel(): Promise<string>;
  export function getBrand(): Promise<string>;
  export function getDeviceName(): Promise<string>;
  export function isEmulator(): Promise<boolean>;
  export function getUniqueId(): Promise<string>;
  export function getDeviceType(): Promise<string>;
  export function getApplicationName(): string;
  export function getBundleId(): string;

  const DeviceInfo: {
    getVersionSync(): string;
    getBuildNumberSync(): string;
    getDeviceIdSync(): string;
    getSystemVersionSync(): string;
    getModelSync(): string;
    getBrandSync(): string;
    getUniqueIdSync(): string;
    getVersion(): Promise<string>;
    getBuildNumber(): Promise<string>;
    getDeviceId(): Promise<string>;
    getSystemVersion(): Promise<string>;
    getModel(): Promise<string>;
    getBrand(): Promise<string>;
    getDeviceName(): Promise<string>;
    isEmulator(): Promise<boolean>;
    getUniqueId(): Promise<string>;
    getApplicationName(): string;
    getBundleId(): string;
  };
  export default DeviceInfo;
}

declare module 'react-native-locale' {
  export function getLocale(): string;
  export function getPreferredLocales(): string[];
}

declare module 'react-native-mixpanel' {
  export function sharedInstanceWithToken(token: string): void;
  export function track(event: string): void;
  export function trackWithProperties(event: string, properties: object): void;
  export function identify(id: string): void;
  export function set(properties: object): void;
  export function setOnce(properties: object): void;
  export function registerSuperProperties(properties: object): void;
  export function setPushRegistrationId(token: string): void;
  export function addPushDeviceToken(token: string): void;
  export function reset(): void;
  export function timeEvent(event: string): void;

  const Mixpanel: {
    sharedInstanceWithToken(token: string): void;
    track(event: string): void;
    trackWithProperties(event: string, properties: object): void;
    identify(id: string): void;
    set(properties: object): void;
    setOnce(properties: object): void;
    registerSuperProperties(properties: object): void;
    setPushRegistrationId(token: string): void;
    addPushDeviceToken(token: string): void;
    reset(): void;
    timeEvent(event: string): void;
  };
  export default Mixpanel;
}

// react-native-permissions v4 API
declare module 'react-native-permissions' {
  // Permission results
  export const RESULTS: {
    UNAVAILABLE: 'unavailable';
    DENIED: 'denied';
    BLOCKED: 'blocked';
    GRANTED: 'granted';
    LIMITED: 'limited';
  };

  type PermissionStatus = 'unavailable' | 'denied' | 'blocked' | 'granted' | 'limited';

  // iOS Permissions
  export const PERMISSIONS: {
    IOS: {
      APP_TRACKING_TRANSPARENCY: string;
      BLUETOOTH_PERIPHERAL: string;
      CALENDARS: string;
      CAMERA: string;
      CONTACTS: string;
      FACE_ID: string;
      LOCATION_ALWAYS: string;
      LOCATION_WHEN_IN_USE: string;
      MEDIA_LIBRARY: string;
      MICROPHONE: string;
      MOTION: string;
      PHOTO_LIBRARY: string;
      PHOTO_LIBRARY_ADD_ONLY: string;
      REMINDERS: string;
      SIRI: string;
      SPEECH_RECOGNITION: string;
      STOREKIT: string;
    };
    ANDROID: {
      ACCEPT_HANDOVER: string;
      ACCESS_BACKGROUND_LOCATION: string;
      ACCESS_COARSE_LOCATION: string;
      ACCESS_FINE_LOCATION: string;
      ACCESS_MEDIA_LOCATION: string;
      ACTIVITY_RECOGNITION: string;
      ADD_VOICEMAIL: string;
      ANSWER_PHONE_CALLS: string;
      BLUETOOTH_ADVERTISE: string;
      BLUETOOTH_CONNECT: string;
      BLUETOOTH_SCAN: string;
      BODY_SENSORS: string;
      BODY_SENSORS_BACKGROUND: string;
      CALL_PHONE: string;
      CAMERA: string;
      GET_ACCOUNTS: string;
      NEARBY_WIFI_DEVICES: string;
      POST_NOTIFICATIONS: string;
      PROCESS_OUTGOING_CALLS: string;
      READ_CALENDAR: string;
      READ_CALL_LOG: string;
      READ_CONTACTS: string;
      READ_EXTERNAL_STORAGE: string;
      READ_MEDIA_AUDIO: string;
      READ_MEDIA_IMAGES: string;
      READ_MEDIA_VIDEO: string;
      READ_PHONE_NUMBERS: string;
      READ_PHONE_STATE: string;
      READ_SMS: string;
      RECEIVE_MMS: string;
      RECEIVE_SMS: string;
      RECEIVE_WAP_PUSH: string;
      RECORD_AUDIO: string;
      SEND_SMS: string;
      USE_SIP: string;
      UWB_RANGING: string;
      WRITE_CALENDAR: string;
      WRITE_CALL_LOG: string;
      WRITE_CONTACTS: string;
      WRITE_EXTERNAL_STORAGE: string;
    };
  };

  export function check(permission: string): Promise<PermissionStatus>;
  export function request(permission: string): Promise<PermissionStatus>;
  export function checkMultiple(permissions: string[]): Promise<Record<string, PermissionStatus>>;
  export function requestMultiple(permissions: string[]): Promise<Record<string, PermissionStatus>>;
  export function openSettings(): Promise<void>;
  export function checkNotifications(): Promise<{ status: PermissionStatus; settings: object }>;
  export function requestNotifications(options: string[]): Promise<{ status: PermissionStatus; settings: object }>;
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

  // GeocodingObject is designed to be compatible with Address from formatAddress.ts
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
    // Optional properties to match Address interface
    locale?: string;
    thoroughfare?: string | null;
    subThoroughfare?: string | null;
    administrativeArea?: string | null;
    subAdministrativeArea?: string | null;
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
  interface CalendarEventOptions {
    title: string;
    description?: string;
    startDate: string;
    endDate: string;
    location?: string;
    recurrence?: string;
  }

  export function openCalendar(): void;
  export function openMaps(address: string): void;
  export function openMapsWithRoute(address: string, mode: string): void;
  export function sendPhoneDial(phoneNumber: string): void;
  export function sendSms(phoneNumber: string, body: string): void;
  export function sendMail(email: string, options: { subject?: string; body?: string }): void;
  export function openApp(packageName: string, extras?: object): Promise<boolean>;
  export function openAppWithData(packageName: string, dataUri: string): Promise<boolean>;
  export function addCalendarEvent(options: CalendarEventOptions): void;

  const SendIntentAndroid: {
    openCalendar(): void;
    openMaps(address: string): void;
    openMapsWithRoute(address: string, mode: string): void;
    sendPhoneDial(phoneNumber: string): void;
    sendSms(phoneNumber: string, body: string): void;
    sendMail(email: string, options: { subject?: string; body?: string }): void;
    openApp(packageName: string, extras?: object): Promise<boolean>;
    openAppWithData(packageName: string, dataUri: string): Promise<boolean>;
    addCalendarEvent(options: CalendarEventOptions): void;
  };
  export default SendIntentAndroid;
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

// React Navigation v6
declare module '@react-navigation/native' {
  import * as React from 'react';

  export interface NavigationState {
    index: number;
    routes: { name: string; key: string; params?: object }[];
  }

  export interface NavigationContainerRef<ParamList = object> {
    navigate<RouteName extends keyof ParamList>(
      name: RouteName,
      params?: ParamList[RouteName]
    ): void;
    goBack(): void;
    reset(state: NavigationState): void;
    getCurrentRoute(): { name: string; params?: object } | undefined;
  }

  export interface NavigationContainerProps {
    ref?: React.RefObject<NavigationContainerRef<any>>;
    onStateChange?: (state: NavigationState | undefined) => void;
    children?: React.ReactNode;
  }

  export const NavigationContainer: React.FC<NavigationContainerProps>;

  export function useNavigation<T = any>(): T;
  export function useRoute<T = any>(): T;
  export function useFocusEffect(callback: () => void | (() => void)): void;
  export function useIsFocused(): boolean;
}

declare module '@react-navigation/stack' {
  import * as React from 'react';

  export interface StackNavigationOptions {
    title?: string;
    headerTitle?: string | (() => React.ReactNode);
    headerLeft?: () => React.ReactNode;
    headerRight?: () => React.ReactNode;
    headerTintColor?: string;
    headerStyle?: object;
    headerShown?: boolean;
    cardStyle?: object;
    gestureEnabled?: boolean;
  }

  export interface StackScreenProps<ParamList extends object, RouteName extends keyof ParamList = keyof ParamList> {
    navigation: {
      navigate<T extends keyof ParamList>(name: T, params?: ParamList[T]): void;
      goBack(): void;
      setParams(params: Partial<ParamList[RouteName]>): void;
      setOptions(options: Partial<StackNavigationOptions>): void;
    };
    route: {
      key: string;
      name: RouteName;
      params: ParamList[RouteName];
    };
  }

  export interface StackNavigatorProps {
    initialRouteName?: string;
    screenOptions?: StackNavigationOptions;
    children: React.ReactNode;
  }

  export interface StackScreenConfig {
    name: string;
    component: React.ComponentType<any>;
    options?: StackNavigationOptions | ((props: any) => StackNavigationOptions);
  }

  export function createStackNavigator<ParamList extends object = object>(): {
    Navigator: React.ComponentType<StackNavigatorProps>;
    Screen: React.ComponentType<StackScreenConfig>;
    Group: React.ComponentType<{ children: React.ReactNode }>;
  };
}

declare module '@react-navigation/bottom-tabs' {
  import * as React from 'react';

  export interface BottomTabNavigationOptions {
    title?: string;
    tabBarIcon?: (props: { focused: boolean; color: string; size: number }) => React.ReactNode;
    tabBarLabel?: string | ((props: { focused: boolean; color: string }) => React.ReactNode);
    tabBarActiveTintColor?: string;
    tabBarInactiveTintColor?: string;
    tabBarStyle?: object;
    headerShown?: boolean;
  }

  export interface BottomTabScreenProps<ParamList extends object, RouteName extends keyof ParamList = keyof ParamList> {
    navigation: {
      navigate<T extends keyof ParamList>(name: T, params?: ParamList[T]): void;
      goBack(): void;
    };
    route: {
      key: string;
      name: RouteName;
      params: ParamList[RouteName];
    };
  }

  export interface BottomTabNavigatorProps {
    initialRouteName?: string;
    screenOptions?: BottomTabNavigationOptions;
    children: React.ReactNode;
  }

  export function createBottomTabNavigator<ParamList extends object = object>(): {
    Navigator: React.ComponentType<BottomTabNavigatorProps>;
    Screen: React.ComponentType<{
      name: string;
      component: React.ComponentType<any>;
      options?: BottomTabNavigationOptions | ((props: any) => BottomTabNavigationOptions);
    }>;
  };
}

// Firebase - Modular @react-native-firebase/* packages
declare module '@react-native-firebase/analytics' {
  interface FirebaseAnalyticsModule {
    logEvent(name: string, params?: Record<string, unknown>): Promise<void>;
    setUserProperty(name: string, value: string | null): Promise<void>;
    setUserId(id: string | null): Promise<void>;
    setCurrentScreen(screenName: string, screenClass?: string): Promise<void>;
    setAnalyticsCollectionEnabled(enabled: boolean): Promise<void>;
  }

  function analytics(): FirebaseAnalyticsModule;
  export default analytics;
}

declare module '@react-native-firebase/remote-config' {
  interface ConfigValue {
    asString(): string;
    asNumber(): number;
    asBoolean(): boolean;
    getSource(): 'default' | 'remote' | 'static';
  }

  interface ConfigSettings {
    minimumFetchIntervalMillis?: number;
    fetchTimeoutMillis?: number;
  }

  interface FirebaseRemoteConfigModule {
    setConfigSettings(settings: ConfigSettings): Promise<void>;
    setDefaults(defaults: Record<string, unknown>): Promise<void>;
    fetch(expirationDuration?: number): Promise<void>;
    fetchAndActivate(): Promise<boolean>;
    activate(): Promise<boolean>;
    getValue(key: string): ConfigValue;
    getAll(): Record<string, ConfigValue>;
  }

  function remoteConfig(): FirebaseRemoteConfigModule;
  export default remoteConfig;
}

declare module '@react-native-firebase/database' {
  export namespace FirebaseDatabaseTypes {
    interface DataSnapshot {
      val(): unknown;
      key: string | null;
      exists(): boolean;
      forEach(action: (snapshot: DataSnapshot) => boolean | void): boolean;
      child(path: string): DataSnapshot;
      hasChild(path: string): boolean;
      hasChildren(): boolean;
      numChildren(): number;
      ref: Reference;
    }

    interface Reference {
      on(eventType: string, callback: (snapshot: DataSnapshot) => void): () => void;
      off(eventType?: string, callback?: (snapshot: DataSnapshot) => void): void;
      once(eventType: string): Promise<DataSnapshot>;
      set(value: unknown): Promise<void>;
      update(values: object): Promise<void>;
      remove(): Promise<void>;
      push(value?: unknown): Reference;
      child(path: string): Reference;
      key: string | null;
      parent: Reference | null;
      root: Reference;
    }
  }

  interface FirebaseDatabaseModule {
    ref(path?: string): FirebaseDatabaseTypes.Reference;
    goOnline(): void;
    goOffline(): void;
    setPersistenceEnabled(enabled: boolean): Promise<void>;
  }

  function database(): FirebaseDatabaseModule;
  export default database;
  export { FirebaseDatabaseTypes };
}

declare module '@react-native-firebase/app' {
  interface FirebaseApp {
    name: string;
    options: {
      apiKey: string;
      appId: string;
      projectId: string;
      databaseURL?: string;
      storageBucket?: string;
      messagingSenderId?: string;
    };
  }

  const firebase: {
    app(name?: string): FirebaseApp;
    apps: FirebaseApp[];
  };
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

declare module '@sentry/react-native' {
  interface SentryInitOptions {
    dsn: string;
    debug?: boolean;
    environment?: string;
    release?: string;
    dist?: string;
    tracesSampleRate?: number;
    sampleRate?: number;
    enableNativeCrashHandling?: boolean;
    enableAutoSessionTracking?: boolean;
    sessionTrackingIntervalMillis?: number;
    attachStacktrace?: boolean;
    attachScreenshot?: boolean;
    beforeSend?: (event: any) => any | null;
    beforeBreadcrumb?: (breadcrumb: any) => any | null;
    integrations?: any[];
  }

  export function init(options: SentryInitOptions): void;
  export function captureException(error: Error | string, captureContext?: object): string;
  export function captureMessage(message: string, level?: string): string;
  export function captureEvent(event: object): string;
  export function setUser(user: { id?: string; email?: string; username?: string } | null): void;
  export function setTag(key: string, value: string): void;
  export function setTags(tags: Record<string, string>): void;
  export function setExtra(key: string, value: any): void;
  export function setExtras(extras: Record<string, any>): void;
  export function setContext(name: string, context: Record<string, any> | null): void;
  export function addBreadcrumb(breadcrumb: { message?: string; category?: string; level?: string; data?: object }): void;
  export function configureScope(callback: (scope: any) => void): void;
  export function withScope(callback: (scope: any) => void): void;
  export function startTransaction(context: { name: string; op?: string }): any;
  export function flush(timeout?: number): Promise<boolean>;
  export function close(timeout?: number): Promise<boolean>;

  // React Native specific
  export function wrap<P>(RootComponent: React.ComponentType<P>): React.ComponentType<P>;
  export function nativeCrash(): void;
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

  // Details object for saveEvent - title is passed as separate first parameter
  interface CalendarEventDetails {
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
  export function saveEvent(title: string, details: CalendarEventDetails): Promise<string>;
  export function removeEvent(id: string): Promise<boolean>;
}

// Google API
declare module 'react-native-google-api-availability' {
  export function checkGooglePlayServices(): Promise<string>;
  export function promptGooglePlayUpdate(showDialog?: boolean): Promise<number>;
}

// Segmented control
declare module '@react-native-segmented-control/segmented-control' {
  import * as React from 'react';
  import { StyleProp, ViewStyle } from 'react-native';

  interface SegmentedControlProps {
    values: string[];
    selectedIndex?: number;
    onChange?: (event: { nativeEvent: { selectedSegmentIndex: number } }) => void;
    tintColor?: string;
    enabled?: boolean;
    style?: StyleProp<ViewStyle>;
  }

  export default class SegmentedControl extends React.Component<SegmentedControlProps> {}
}

declare module 'react-native-segmented-android' {
  import * as React from 'react';

  interface SegmentedControlAndroidProps {
    childText?: string[];
    orientation?: 'horizontal' | 'vertical';
    onChange?: (event: { selected: number }) => void;
    tintColor?: string[];
    selectedPosition?: number;
    style?: object;
  }

  export default class SegmentedControlAndroid extends React.Component<SegmentedControlAndroidProps> {}
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
    protocol?: string | null;
    slashes?: boolean | null;
    auth?: string | null;
    host?: string | null;
    port?: string | null;
    hostname?: string | null;
    hash?: string | null;
    search?: string | null;
    query?: string | Record<string, string | undefined> | null;
    pathname?: string | null;
    path?: string | null;
    href?: string;
  }

  export function parse(urlStr: string, parseQueryString?: boolean, slashesDenoteHost?: boolean): UrlObject;
  export function format(urlObj: UrlObject): string;
  export function resolve(from: string, to: string): string;

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
    addBatchCallback(callback: (error: unknown, results: unknown[]) => void): GraphRequestManager;
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

  export const MessageDialog: {
    canShow(content: ShareContent): Promise<boolean>;
    show(content: ShareContent): Promise<{ postId?: string }>;
  };

  export const AppEventsLogger: {
    logEvent(eventName: string, valueToSum?: number, params?: Record<string, unknown>): void;
    logPurchase(purchaseAmount: number, currency: string, params?: Record<string, unknown>): void;
    flush(): void;
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
    scrollEnabled?: boolean;
    formStyles?: object;
    navigator?: object;
    onValueChange?: (values: object) => void;
  }

  interface SubmitWidgetProps {
    title?: string;
    isDisabled?: boolean;
    activityIndicatorColor?: string;
    onSubmit?: (
      isValid: boolean,
      values: object,
      validationResults: any,
      postSubmit?: ((errors?: string[]) => void) | null,
      modalNavigator?: any
    ) => void | Promise<void>;
  }

  interface SubmitWidgetState {
    isLoading: boolean;
  }

  export class SubmitWidget extends React.Component<SubmitWidgetProps, SubmitWidgetState> {
    getStyle(name: string): object;
    _doSubmit(): void;
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
    static SubmitWidget: typeof SubmitWidget;
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

// Legacy react-navigation v1 types for backward compatibility
declare module 'react-navigation/src/TypeDefinition' {
  import * as React from 'react';

  export interface NavigationAction {
    type: string;
    [key: string]: unknown;
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

  export interface NavigationScene {
    route: NavigationRoute;
    index: number;
    focused: boolean;
    tintColor?: string;
  }

  export interface NavigationSceneRendererProps {
    scene: NavigationScene;
    scenes: NavigationScene[];
    index: number;
    navigation: NavigationScreenProp<any>;
    position: any;
  }

  export interface NavigationScreenProp<S> {
    state: S;
    dispatch: (action: NavigationAction) => boolean;
    goBack: (routeKey?: string | null) => boolean;
    navigate: (routeName: string, params?: object, action?: NavigationAction) => boolean;
    setParams: (newParams: object) => boolean;
  }

  export interface NavigationParams {
    [key: string]: unknown;
  }
}

declare module 'react-navigation' {
  export * from 'react-navigation/src/TypeDefinition';
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
    formatDate(value: Date | number | unknown, options?: Intl.DateTimeFormatOptions): string;
    formatTime(value: Date | number | unknown, options?: Intl.DateTimeFormatOptions): string;
    formatRelativeTime?(value: number, unit?: string, options?: object): string;
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
