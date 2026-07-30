import React, { useReducer } from 'react';
import { deeplyMerge } from '@saurookkadookk/node-utils';

import type { AppDispatch, KeyedObject } from '@/types';
import type { CombinedStateSliceReducer } from '@/store';

export default function AppStateProviderHOC<
  State extends KeyedObject, // force formatting
>({
  StateContext,
  DispatchContext,
  combinedReducer,
}: {
  StateContext: React.Context<State>;
  DispatchContext: React.Context<AppDispatch>;
  combinedReducer: CombinedStateSliceReducer<State>;
}) {
  return function AppStateProvider({
    children, // force formatting
    initialState,
  }: React.PropsWithChildren<{
    initialState?: State;
  }>) {
    const [combinedReducerFunc, combinedDefaultState] = combinedReducer;

    const mergedDefaultState = deeplyMerge(
      {},
      combinedDefaultState,
      initialState ?? {},
    ) as State;
    const [state, dispatch] = useReducer(combinedReducerFunc, mergedDefaultState);

    return (
      <StateContext.Provider value={state}>
        <DispatchContext.Provider value={dispatch}>{children}</DispatchContext.Provider>
      </StateContext.Provider>
    );
  };
}
