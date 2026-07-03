import React, { useReducer } from 'react';

import type { CombinedStateSliceReducer, KeyedObject } from '@/types';
import { deeplyMerge } from '@/common/utils';

export default function AppStateProviderHOC<
  State extends KeyedObject = KeyedObject, // force formatting
  ReducerAction = any,
>({
  StateContext,
  DispatchContext,
  combinedReducer,
}: {
  StateContext: React.Context<State>;
  DispatchContext: React.Context<React.Dispatch<ReducerAction>>;
  combinedReducer: CombinedStateSliceReducer;
}) {
  return function AppStateProvider({
    children, // force formatting
    initialState,
  }: {
    children: React.ReactElement;
    initialState?: State;
  }) {
    const [combinedReducerFunc, combinedDefaultState] = combinedReducer;

    const mergedDefaultState = deeplyMerge<State>({}, combinedDefaultState);
    const recursivelyMergedState = deeplyMerge<State>(
      mergedDefaultState,
      initialState ?? {},
    );
    const [state, dispatch] = useReducer(combinedReducerFunc, recursivelyMergedState);

    return (
      <StateContext.Provider value={state}>
        <DispatchContext.Provider value={dispatch}>{children}</DispatchContext.Provider>
      </StateContext.Provider>
    );
  };
}
