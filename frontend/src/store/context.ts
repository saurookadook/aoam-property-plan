import { createContext, type Dispatch } from 'react';

import type { AppState, ReducerAction } from '@/types';

export const AppStateContext = createContext<AppState>({} as AppState);
export const AppDispatchContext = createContext<Dispatch<ReducerAction>>(
  (action) => action,
);
