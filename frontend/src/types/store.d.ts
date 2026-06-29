import type { MarketsStateSlice } from '@/store/markets/reducer';
import { KeyedObject, ValueOf } from '@/types/main';

/**********************************************************************
 * Generic State Store Types
 **********************************************************************/
export type AppState = {
  markets: MarketsStateSlice;
};

export type ReducerAction<T = ValueOf<AppState>> = {
  type: string;
  payload?: T;
};

export type AppDispatch = React.Dispatch<ReducerAction>;

interface CombinedState extends StateSlice {
  pageData?: StateSlice;
}

type GenericReducerFunc<S, A> = (state: S, action: A) => S;

type StateSliceReducerFunc = (state: StateSlice, action: ReducerAction) => StateSlice;

export type StateSliceReducer<S, A> = [GenericReducerFunc<S, A>, S];

export type CombinedStateSliceReducer = [GenericReducerFunc, CombinedState];
