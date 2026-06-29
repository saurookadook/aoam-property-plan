import { createContext, type Dispatch } from 'react';

import type { AppState, ReducerAction } from '@/types';

export const BaseStateContext = createContext<AppState>({} as AppState);
export const BaseDispatchContext = createContext<Dispatch<ReducerAction>>(
  (action) => action,
);
