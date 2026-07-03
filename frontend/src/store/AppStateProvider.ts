import type { AppState } from '@/types';
import AppStateProviderHOC from './AppStateProviderHOC';
import { AppStateContext, AppDispatchContext } from './context';
import { default as appStateReducer } from './reducer';

export const AppStateProvider = AppStateProviderHOC<AppState>({
  StateContext: AppStateContext,
  DispatchContext: AppDispatchContext,
  combinedReducer: appStateReducer,
});
