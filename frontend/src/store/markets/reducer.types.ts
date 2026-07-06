import type CombineReducers from '@saurookkadookk/react-utils-combine-reducers';

import type { MarketEntity, Nullable, ReducerAction } from '@/types';

export type MarketsStateSlice = {
  marketsList: Nullable<MarketEntity[]>;
};

export type MarketsAction = ReducerAction<Partial<MarketsStateSlice>>;

export type CombinedMarketsStateSlice = {
  marketsList: CombineReducers.ArgsTuple<
    MarketsStateSlice['marketsList'],
    MarketsAction
  >;
};
