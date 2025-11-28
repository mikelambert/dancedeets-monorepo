/**
 * Copyright 2016 DanceDeets.
 */

import type { Action } from '../actions/types';

interface State {
  videoIndex: number;
}

const initialState: State = {
  videoIndex: 0,
};

export function tutorials(state: State = initialState, action: Action): State {
  if (action.type === 'TUTORIAL_SET_VIDEO_INDEX') {
    return {
      ...state,
      videoIndex: action.index,
    };
  }
  return state;
}
