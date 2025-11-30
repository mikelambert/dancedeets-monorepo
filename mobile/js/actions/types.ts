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
 */

import { AccessToken } from 'react-native-fbsdk';
import type { ThunkDispatch, ThunkAction as ReduxThunkAction } from 'redux-thunk';
import type { AnyAction } from 'redux';
import type { Event } from 'dancedeets-common/js/events/models';
import type { search as searchApi } from '../api/dancedeets';
import type { AddEventList, SortOrder } from '../addEventsModels';
import type { State as SearchHeaderState } from '../ducks/searchHeader';

// Use the mobile-specific search response type
type MobileSearchResponse = Awaited<ReturnType<typeof searchApi>>;

export interface User {
  profile: {
    id: string;
    name: string;
  };
  picture: { data: { url: string } };
  friends: {
    data: Array<{ id: string }>;
  };
  ddUser: {
    location: string;
    formattedCity?: string;
    num_hand_added_events?: number;
    num_auto_added_events?: number;
  };
}

export type Action =
  | { type: 'LOGIN_START_ONBOARD' }
  | { type: 'LOGIN_LOGGED_IN'; token: AccessToken }
  | { type: 'LOGIN_LOGGED_OUT' }
  | { type: 'LOGIN_LOADED_USER'; user: User }
  | { type: 'LOGIN_SKIPPED' }
  | { type: 'DETECTED_LOCATION'; location: string }
  | { type: 'START_SEARCH' }
  | { type: 'SEARCH_COMPLETE'; response: MobileSearchResponse }
  | { type: 'SEARCH_FAILED'; errorString: string | null }
  | { type: 'WAITING_FOR_LOCATION'; waiting: boolean }
  | { type: 'searchHeader/START_OPEN' }
  | { type: 'searchHeader/FINISH_OPEN' }
  | { type: 'searchHeader/START_CLOSE' }
  | { type: 'searchHeader/FINISH_CLOSE' }
  | { type: 'textInputs/DETECTED_LOCATION'; location: string }
  | { type: 'textInputs/UPDATE_LOCATION'; location: string }
  | { type: 'textInputs/UPDATE_KEYWORDS'; keywords: string }
  | { type: 'LOAD_EVENT_START'; eventId: string }
  | { type: 'LOAD_EVENT_DONE'; eventId: string; event: Event }
  | { type: 'ADD_EVENTS_RELOAD' }
  | { type: 'ADD_EVENTS_RELOAD_COMPLETE'; results: AddEventList }
  | { type: 'ADD_EVENTS_RELOAD_FAILED' }
  | {
      type: 'ADD_EVENTS_UPDATE_LOADED';
      status: 'PENDING' | 'LOADED' | 'UNLOADED' | 'CLICKED';
      eventId: string;
    }
  | { type: 'ADD_EVENTS_SET_ONLY_UNADDED'; value: boolean }
  | { type: 'ADD_EVENTS_SET_SORT_ORDER'; value: SortOrder }
  | { type: 'SET_CURRENT_LOCALE'; locale: string }
  | { type: 'TRANSLATE_EVENT_TOGGLE'; eventId: string }
  | { type: 'TRANSLATE_EVENT_DONE'; eventId: string; translations: { name: string; description: string } }
  | { type: 'TUTORIAL_SET_VIDEO_INDEX'; index: number }
  | { type: 'FIREBASE_UPDATE'; key: string; value: unknown };

export interface RootState {
  user: {
    userData: User | null;
    isLoggedIn: boolean;
  };
  search: {
    response: MobileSearchResponse | null;
    loading: boolean;
    error: boolean;
    errorString: string | null;
  };
  addEvents: {
    results: AddEventList | null;
    loading: boolean;
  };
  firebase: Record<string, unknown>;
  translate: {
    events: Record<string, { visible: boolean; translation: { name: string; description: string } }>;
  };
  tutorials: {
    videoIndex: number;
  };
  loadedEvents: Record<string, Event>;
  searchHeader: SearchHeaderState;
}

export type GetState = () => RootState;

// Use ThunkDispatch for proper compatibility with react-redux connect
export type Dispatch = ThunkDispatch<RootState, undefined, AnyAction>;

// ThunkAction compatible with redux-thunk
export type ThunkAction = ReduxThunkAction<unknown, RootState, undefined, AnyAction>;

export type PromiseAction = Promise<Action>;
