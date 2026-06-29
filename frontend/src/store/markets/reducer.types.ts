import type CombineReducers from '@saurookkadookk/react-utils-combine-reducers';

import type { Nullable } from '@/types';

export type MarketsStateSlice = {
  marketsList: Nullable<any[]>;
};

export type MarketsAction = CombineReducers.ReducerAction<{
  marketsList?: MarketsStateSlice['marketsList'];
}>;

export type CombinedMarketsStateSlice = {
  marketsList: CombineReducers.ArgsTuple<
    MarketsStateSlice['marketsList'],
    MarketsAction
  >;
};
