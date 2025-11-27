/**
 * Global Window interface extensions.
 */

declare global {
  interface FBAuthResponse {
    status: 'connected' | 'not_authorized' | 'unknown';
    authResponse?: {
      accessToken: string;
      userID: string;
    };
  }

  interface FacebookSDK {
    init(options: {
      version: string;
      appId: string;
      status: boolean;
      cookie: boolean;
      xfbml: boolean;
    }): void;
    login(callback: (response: FBAuthResponse) => void, options: { scope: string }): void;
    logout(callback: (response: unknown) => void): void;
    getLoginStatus(callback: (response: FBAuthResponse) => void): void;
    Event: {
      subscribe(event: string, callback: (response: FBAuthResponse) => void): void;
    };
    XFBML: {
      parse(): void;
    };
  }

  interface Window {
    FB?: FacebookSDK;
    fbAsyncInit?: () => void;
    hasCalledFbInit?: boolean;
    mixpanel?: {
      track(event: string): void;
    };
    prodMode?: boolean;
    adsbygoogle?: Record<string, unknown>[];
    _REACT_PROPS?: Record<string, unknown>;
    _REACT_ID?: string;
    fbPermissions?: string;
    fbAppId?: string;
    baseHostname?: string;
    showSmartBanner?: boolean;
  }
}

export {};
