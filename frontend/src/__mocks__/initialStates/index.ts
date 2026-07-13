import type { AppState } from '@/store';
import { deeplyMerge } from '@/common/utils';

export function createDefaultInitialState(overrides: Partial<AppState> = {}): AppState {
  return deeplyMerge<AppState>(
    {
      markets: {
        marketsList: null,
      },
    },
    overrides,
  );
}
