/**
 * Copyright 2016 Facebook, Inc.
 *
 * You are hereby granted a non-exclusive, worldwide, royalty-free license to
 * use, copy, modify, and distribute this software in source code or binary
 * form for use in connection with the web services and APIs provided by
 * Facebook.
 *
 * As with any software that integrates with the Facebook platform, your use
 * of this software is subject to the Facebook Developer Principles and
 * Policies [http://developers.facebook.com/policy/]. This copyright notice
 * shall be included in all copies or substantial portions of the software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE
 *
 * @flow
 */

'use strict';

import type { NavigationRoute } from 'NavigationTypeDefinition';
import { AccessToken } from 'react-native-fbsdk';
import type { SearchResults } from '../events/search';
import type { AddEventList, SortOrder } from '../addEventsModels';

export type User = {
  profile: any;
  picture: {data: {url: string}};
  friends: any;
  ddUser: any;
};

export type Action =
    { type: 'NAV_PUSH', navigator: string, state: NavigationRoute }
  | { type: 'NAV_POP', navigator: string }
  | { type: 'NAV_JUMP_TO_KEY', navigator: string, key: string }
  | { type: 'NAV_JUMP_TO_INDEX', navigator: string, index: number }
  | { type: 'NAV_RESET', navigator: string, index: number, routes: Array<NavigationRoute> }
  | { type: 'NAV_SWAP', navigator: string, key: string, newState: NavigationRoute }
  | { type: 'LOGIN_START_ONBOARD' }
  | { type: 'LOGIN_LOGGED_IN', token: AccessToken }
  | { type: 'LOGIN_LOGGED_OUT' }
  | { type: 'LOGIN_LOADED_USER', user: User }
  | { type: 'LOGIN_SKIPPED' }
  | { type: 'DETECTED_LOCATION', location: string }
  | { type: 'TOGGLE_LAYOUT' }
  | { type: 'UPDATE_LOCATION', location: string }
  | { type: 'UPDATE_KEYWORDS', keywords: string }
  | { type: 'START_SEARCH' }
  | { type: 'SEARCH_COMPLETE', results: SearchResults }
  | { type: 'SEARCH_FAILED' }
  | { type: 'ADD_EVENTS_RELOAD' }
  | { type: 'ADD_EVENTS_RELOAD_COMPLETE', results: AddEventList }
  | { type: 'ADD_EVENTS_RELOAD_FAILED' }
  | { type: 'ADD_EVENTS_UPDATE_LOADED',
      status: 'PENDING' | 'LOADED' | 'UNLOADED',
      eventId: string }
  | { type: 'ADD_EVENTS_SET_ONLY_UNADDED', value: boolean }
  | { type: 'ADD_EVENTS_SET_SORT_ORDER', value: SortOrder }
  | { type: 'SET_CURRENT_LOCALE', locale: string }
  | { type: 'TRANSLATE_EVENT_TOGGLE', eventId: string }
  | { type: 'TRANSLATE_EVENT_DONE', eventId: string, translations: Object }
  ;

export type Dispatch = (action: Action | ThunkAction | PromiseAction | Array<Action>) => any;
export type GetState = () => Object;
export type ThunkAction = (dispatch: Dispatch, getState: GetState) => any;
export type PromiseAction = Promise<Action>;
