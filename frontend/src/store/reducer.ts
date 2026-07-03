import combineReducers from '@saurookkadookk/react-utils-combine-reducers';

import marketsReducer, { initialMarketsStateSlice } from '@/store/markets/reducer';
import type { AppState } from '@/types';

export const initialAppState: AppState = {
  markets: initialMarketsStateSlice,
};

export default combineReducers({
  markets: marketsReducer,
});
