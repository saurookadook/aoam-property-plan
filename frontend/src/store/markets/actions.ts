import type { AppDispatch } from '@/types';

export const fetchMarkets = async ({ dispatch }: { dispatch: AppDispatch }) => {
  try {
    const response = await fetch('/api/markets');

    // TODO: finish implementing this
  } catch (error) {
    console.warn(
      '[markets : fetchMarkets] - Encountered unexpected exception: ',
      error,
    );
  }
};
