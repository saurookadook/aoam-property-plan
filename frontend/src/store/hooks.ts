import { useContext, useEffect } from 'react';

import { AppStateContext, AppDispatchContext } from './context';

export function useAppStore() {
  const funcName = useAppStore.name;

  const state = useContext(AppStateContext);
  const dispatch = useContext(AppDispatchContext);

  return {
    appState: state, // force formatting
    appDispatch: dispatch,
  };
}
