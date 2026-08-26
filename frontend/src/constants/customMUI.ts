import { type AlertColor } from '@mui/material';

import type { KeyedObject, ValueOf } from '@/types';

export const MUIAlertColor: KeyedObject<AlertColor> = {
  ERROR: 'error',
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
} as const;

export type MUIAlertColorValue = ValueOf<typeof MUIAlertColor>;
