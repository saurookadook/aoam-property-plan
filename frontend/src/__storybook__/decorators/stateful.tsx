import { deeplyMerge } from '@saurookkadookk/node-utils';
import type { Decorator } from '@storybook/react-vite';

import type { AppState } from '@/store';
import { createDefaultInitialState } from '@/__mocks__/initialStates';
import { AppStateProvider } from '@/store';

/**
 * @TODO For some reason, the `mergedInitialState` doesn't seem to be overwriting
 *    certain default state values.
 */
export const MockStoreDecorator =
  (initialState = {}): Decorator =>
  (Story) => {
    const defaultInitialState = createDefaultInitialState();
    const mergedInitialState = deeplyMerge<AppState>(defaultInitialState, initialState);

    return (
      <AppStateProvider initialState={mergedInitialState}>
        <Story />
      </AppStateProvider>
    );
  };
