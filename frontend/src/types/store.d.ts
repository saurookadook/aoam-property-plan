import React from 'react';
import type CombineReducers from '@saurookkadookk/react-utils-combine-reducers';

/**********************************************************************
 * Generic State Store Types
 **********************************************************************/
export type ReducerAction<T = any> = CombineReducers.ReducerAction<T>;

export type AppDispatch<T = any> = React.Dispatch<ReducerAction<T>>;
