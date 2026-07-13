import { createContext, type Dispatch } from 'react';

import type { ReducerAction } from '@/types';
import type { AppState } from './types.d';

export const AppStateContext = createContext<AppState>({} as AppState);
export const AppDispatchContext = createContext<Dispatch<ReducerAction>>(
  (action) => action,
);
