import combineReducers from '@saurookkadookk/react-utils-combine-reducers';

import type { CombinedMarketsStateSlice, MarketsStateSlice } from './reducer.types';

function getInitialMarketsState(): MarketsStateSlice {
  return {
    marketsList: null,
  };
}

export const initialMarketsStateSlice = getInitialMarketsState();

const marketsList: CombinedMarketsStateSlice['marketsList'] = [
  (stateSlice, action) => {
    switch (action.type) {
      default:
        return stateSlice;
    }
  },
  null,
];

export * from './reducer.types';

export default combineReducers({ marketsList });
