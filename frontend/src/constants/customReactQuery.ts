import type {} from // pull type from here?
'@tanstack/react-query';

import type { KeyedObject, ValueOf } from '@/types';

export type ToastStatus = 'error' | 'pending' | 'success';

export const ReactQueryToastStatus: KeyedObject<ToastStatus> = {
  ERROR: 'error',
  PENDING: 'pending',
  SUCCESS: 'success',
} as const;

export type ReactQueryToastStatusValue = ValueOf<typeof ReactQueryToastStatus>;
