/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import EventEmitter from 'eventemitter3';
import Cookies from 'universal-cookie';
import { queryOn } from './dom';

export const fbLoadEmitter = new EventEmitter();

export function fbSetup(
  fbPermissions: string,
  fbAppId: string,
  baseHostname: string
) {
  const cookies = new Cookies();

  let loginPressed = false;

  const cookieOptions = {
    path: '/',
  };
  // Temporary, to ensure we clean up our cookies from our old .dancedeets.com domain
  const cookieOptions2 = {
    domain: '.dancedeets.com',
    path: '/',
  };

  function deleteLoginCookies() {
    [cookieOptions, cookieOptions2].forEach(cookieOpts => {
      cookies.remove(`fbsr_${fbAppId}`, cookieOpts);
      cookies.remove(`fbm_${fbAppId}`, cookieOpts);
      cookies.remove(`user_token_${fbAppId}`, cookieOpts); // set by client, for server
      cookies.remove(`user_login_${fbAppId}`, cookieOpts); // set by server, for client/server
    });
  }

  function reloadWithNewToken() {
    if (String(window.location).indexOf('?') === -1) {
      window.location += '?nt=1';
    } else {
      window.location += '&nt=1';
    }
  }

  function currentUser() {
    const userLogin = cookies.get(`user_login_${fbAppId}`);
    if (userLogin) {
      return userLogin.uid;
    }
    return null;
  }

  function handleStatusChange(response) {
    if (response.status === 'connected') {
      // We want to set this cookie before we attempt to do any reloads below,
      // so that the server will have access to our user_token_ (access token)
      const accessToken = response.authResponse.accessToken;
      cookies.set(`user_token_${fbAppId}`, accessToken, cookieOptions);

      if (response.authResponse.userID !== currentUser()) {
        if (loginPressed) {
          // Only do this for explicit logins, not for auto-logins
          window.mixpanel.track('Login - Completed');
        }
        // reload through endpoint to set up new user cookie serverside
        // TODO(lambert): Add a full-screen overlay explaining what we are doing...
        reloadWithNewToken();
      }
    } else if (response.status === 'not_authorized') {
      // Disabled as long as we have the App Tokens creating logged-in users without a proper FB token
      // if (currentUser()) {
      //   // the user is logged in to Facebook, but not connected to the app
      //   deleteLoginCookies();
      //   // TODO(lambert): Add a full-screen overlay explaining what we are doing...
      //   reloadWithNewToken('not_authorized');
      // }
    } else {
      // the user isn't even logged in to Facebook.

      // This can happen if the user changes their password, and Facebook auto-deletes the Facebook cookie.
      // So delete the user_login_ cookies here, so that we correctly detect a login (when they've re-logged in)
      deleteLoginCookies();
    }
  }

  function initFBCode(FB) {
    function login() {
      loginPressed = true;
      window.mixpanel.track('Login - FBLogin Button Pressed');
      FB.login((/* response */) => {}, {
        scope: fbPermissions,
      });
    }

    function logout() {
      window.mixpanel.track('Logout');
      // Seems the logout callback isn't being called, so ensure we delete the cookie here
      deleteLoginCookies();
      FB.getLoginStatus(response => {
        if (response.status === 'connected') {
          FB.logout(
            (/* response */) => {
              window.location.reload();
            }
          );
        } else {
          window.location.reload();
        }
      });
    }

    FB.init({
      version: 'v2.9',
      appId: fbAppId,
      status: true,
      cookie: true,
      xfbml: true,
    });
    window.hasCalledFbInit = true;
    fbLoadEmitter.emit('fb-load');
    FB.Event.subscribe('auth.statusChange', handleStatusChange);
    FB.getLoginStatus(response => {
      handleStatusChange(response);
    });

    queryOn('.onclick-login', 'click', login);
    queryOn('.onclick-logout', 'click', logout);
  }

  window.fbAsyncInit = () => {
    initFBCode(window.FB);
  };

  /**
   * It'd be nice to stick this in the html page directly, for faster FB loading.
   * But we need this code to run *after* we set window.fbAsyncInit above.
   * TODO: If we want to speed this up, we need to ensure the race conditions
   * can work if FB code loads before this fb.js code (as part of the merged bundle).
   */

  // Facebook/Login Code
  ((d, s, id) => {
    const fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
      return;
    }
    const js = d.createElement(s);
    js.id = id;
    js.src = 'https://connect.facebook.net/en_US/sdk.js';
    if (fjs.parentNode) {
      fjs.parentNode.insertBefore(js, fjs);
    }
  })(document, 'script', 'facebook-jssdk');
}
