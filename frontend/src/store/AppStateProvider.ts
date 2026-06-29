import type { AppState } from '@/types';
import AppStateProviderHOC from './AppStateProviderHOC';
import { BaseStateContext, BaseDispatchContext } from './context';
import { default as appStateReducer } from './reducer';

export const AppStateProvider = AppStateProviderHOC<AppState>({
  StateContext: BaseStateContext,
  DispatchContext: BaseDispatchContext,
  combinedReducer: appStateReducer,
});
