export type KeyedObject<V = any, K = string> = {
  [key in K]: V;
};

export type Nullable<T> = T | null | undefined;

export type ValueOf<T> = T[keyof T];

export type BoundThis = {
  name?: string;
};

export type FixedLengthArray<T, L extends number> = [T, ...T[]] & { length: L };

export * from './custom-embla';
export * from './entity';
export * from './listings';
export * from './markets';
export * from './mirage-server';
export * from './react-custom';
export * from './react-router-custom';
export * from './store';
