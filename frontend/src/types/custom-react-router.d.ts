import type { KeyedObject } from '@/main';

export type AwaitedRouterData<T extends KeyedObject = KeyedObject> = Awaited<
  ReturnType<ReturnType<T>>
>;
