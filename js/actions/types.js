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

import type { NavigationState } from 'NavigationTypeDefinition';
import { Event } from '../models';

export type Action =
    { type: 'NAV_PUSH', state: NavigationState }
  | { type: 'NAV_POP' }
  | { type: 'NAV_JUMP_TO_KEY', key: string }
  | { type: 'NAV_JUMP_TO_INDEX', index: number }
  | { type: 'NAV_RESET', index: number, children: Array<NavigationState> }
  | { type: 'LOGIN_START_ONBOARD' }
  | { type: 'LOGIN_LOGGED_IN' }
  | { type: 'LOGIN_LOGGED_OUT' }
  | { type: 'LOGIN_SKIPPED' }
  | { type: 'VIEW_EVENT', event: Event }
  ;

export type Dispatch = (action: Action | ThunkAction | PromiseAction | Array<Action>) => any;
export type GetState = () => Object;
export type ThunkAction = (dispatch: Dispatch, getState: GetState) => any;
export type PromiseAction = Promise<Action>;
