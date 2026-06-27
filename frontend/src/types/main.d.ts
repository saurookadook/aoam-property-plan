export type KeyedObject<V = any, K = string> = {
  [key in K]: V;
};

export type NullableValue<T> = T | null | undefined;

export type ValueOf<T> = T[keyof T];

export type BoundThis = {
  name?: string;
};

export type FixedLengthArray<T, L extends number> = [T, ...T[]] & { length: L };

export * from './react-custom';
