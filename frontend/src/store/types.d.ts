import type CombineReducers from '@saurookkadookk/react-utils-combine-reducers';

import type { KeyedObject, ReducerAction } from '@/types';
import type { MarketsStateSlice } from '@/store/markets/reducer';

/**
 * @fileoverview Types for the frontend's state store.
 *
 * @NOTE It is not included in `src/types` to prevent it from being included in compiled
 *    output that doesn't require these types.
 *
 */
export interface AppState extends KeyedObject, CombineReducers.AmbiguousObject {
  markets: MarketsStateSlice;
}

export type CombinedStateSliceReducer<State> = [
  CombineReducers.ReducerFunc<State, ReducerAction<State>>,
  State,
];
