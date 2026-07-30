import { deeplyMerge } from '@saurookkadookk/node-utils';

import type { AppState } from '@/store';

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
