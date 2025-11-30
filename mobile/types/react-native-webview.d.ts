declare module 'react-native-webview' {
  import * as React from 'react';
  import { ViewStyle, StyleProp } from 'react-native';

  export interface WebViewSource {
    uri?: string;
    html?: string;
    baseUrl?: string;
  }

  export interface WebViewProps {
    source?: WebViewSource;
    style?: StyleProp<ViewStyle>;
    onNavigationStateChange?: (event: WebViewNavigation) => void;
    onLoad?: (event: WebViewLoadEvent) => void;
    onError?: (event: WebViewErrorEvent) => void;
    onMessage?: (event: WebViewMessageEvent) => void;
    injectedJavaScript?: string;
    javaScriptEnabled?: boolean;
    domStorageEnabled?: boolean;
    startInLoadingState?: boolean;
    scalesPageToFit?: boolean;
    allowsInlineMediaPlayback?: boolean;
    mediaPlaybackRequiresUserAction?: boolean;
    originWhitelist?: string[];
    bounces?: boolean;
    scrollEnabled?: boolean;
    automaticallyAdjustContentInsets?: boolean;
    contentInset?: { top?: number; left?: number; bottom?: number; right?: number };
    onShouldStartLoadWithRequest?: (request: WebViewNavigation) => boolean;
    renderLoading?: () => React.ReactElement;
    renderError?: (errorDomain: string | undefined, errorCode: number, errorDesc: string) => React.ReactElement;
    cacheEnabled?: boolean;
    incognito?: boolean;
    thirdPartyCookiesEnabled?: boolean;
    userAgent?: string;
    applicationNameForUserAgent?: string;
    allowsFullscreenVideo?: boolean;
    allowsBackForwardNavigationGestures?: boolean;
    decelerationRate?: 'normal' | 'fast' | number;
    onLoadStart?: (event: WebViewLoadEvent) => void;
    onLoadEnd?: (event: WebViewLoadEvent) => void;
    onLoadProgress?: (event: WebViewProgressEvent) => void;
    onContentProcessDidTerminate?: (event: WebViewTerminatedEvent) => void;
    mixedContentMode?: 'never' | 'always' | 'compatibility';
    allowUniversalAccessFromFileURLs?: boolean;
    saveFormDataDisabled?: boolean;
    urlPrefixesForDefaultIntent?: string[];
    showsHorizontalScrollIndicator?: boolean;
    showsVerticalScrollIndicator?: boolean;
    directionalLockEnabled?: boolean;
    geolocationEnabled?: boolean;
    allowFileAccess?: boolean;
    pullToRefreshEnabled?: boolean;
    ignoreSilentHardwareSwitch?: boolean;
    onFileDownload?: (event: { nativeEvent: { downloadUrl: string } }) => void;
    limitsNavigationsToAppBoundDomains?: boolean;
    textZoom?: number;
    mediaCapturePermissionGrantType?: 'prompt' | 'grant' | 'deny' | 'grantIfSameHostElsePrompt' | 'grantIfSameHostElseDeny';
    autoManageStatusBarEnabled?: boolean;
    setSupportMultipleWindows?: boolean;
    enableApplePay?: boolean;
    minimumFontSize?: number;
    forceDarkOn?: boolean;
    menuItems?: Array<{ label: string; key: string }>;
    onCustomMenuSelection?: (event: { nativeEvent: { label: string; key: string; selectedText: string } }) => void;
    basicAuthCredential?: { username: string; password: string };
    fraudulentWebsiteWarningEnabled?: boolean;
    children?: React.ReactNode;
  }

  export interface WebViewNavigation {
    url: string;
    title: string;
    loading: boolean;
    canGoBack: boolean;
    canGoForward: boolean;
    lockIdentifier?: number;
    navigationType?: string;
    mainDocumentURL?: string;
  }

  export interface WebViewLoadEvent {
    nativeEvent: WebViewNavigation;
  }

  export interface WebViewErrorEvent {
    nativeEvent: WebViewNavigation & {
      description: string;
      code: number;
      domain?: string;
    };
  }

  export interface WebViewMessageEvent {
    nativeEvent: {
      data: string;
    };
  }

  export interface WebViewProgressEvent {
    nativeEvent: {
      progress: number;
    };
  }

  export interface WebViewTerminatedEvent {
    nativeEvent: {
      syntheticEvent: boolean;
    };
  }

  export class WebView extends React.Component<WebViewProps> {
    goBack: () => void;
    goForward: () => void;
    reload: () => void;
    stopLoading: () => void;
    injectJavaScript: (script: string) => void;
    requestFocus: () => void;
    postMessage: (message: string) => void;
    clearFormData: () => void;
    clearCache: (includeDiskFiles: boolean) => void;
    clearHistory: () => void;
  }

  export default WebView;
}
