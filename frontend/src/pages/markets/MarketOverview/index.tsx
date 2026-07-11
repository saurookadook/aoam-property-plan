import { useLoaderData, type LoaderFunctionArgs } from 'react-router';
import {
  QueryClient,
  queryOptions,
  useQuery,
  useSuspenseQuery,
} from '@tanstack/react-query';

import type { MarketEntity } from '@/types';
import { LoadingState } from '@/common/components';
import { API_SERVER_DOMAIN } from '@/constants';
import { FlexColumn } from '@/layouts';
import { fetchy } from '@/utils';

import './styles.scss';

export const marketOverviewQuery = (marketId: string) =>
  queryOptions({
    queryKey: ['marketOverview', marketId],
    queryFn: async () => {
      const marketOverviewResponse = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/markets/${marketId}`) // force formatting
        .then((res) => res.json());

      return { marketOverview: marketOverviewResponse.data as MarketEntity };
    },
  });

export const marketOverviewLoader =
  (_queryClient: QueryClient) =>
  async ({ params }: LoaderFunctionArgs) => {
    if (!params.marketId) {
      throw new Error("No 'marketId' param provided!");
    }

    await _queryClient.ensureQueryData(marketOverviewQuery(params.marketId));
    return { marketId: params.marketId };
  };

export function MarketOverview() {
  const { marketId } = useLoaderData() as Awaited<
    ReturnType<ReturnType<typeof marketOverviewLoader>>
  >;
  const { data, error, isFetching, status } = useSuspenseQuery(
    marketOverviewQuery(marketId),
  );

  return (
    <FlexColumn id="market-overview">
      <h2>{`Market Overview: ${marketId}`}</h2>

      <FlexColumn className="markets-list__wrapper">
        {isFetching ? (
          <div className="loading-state__wrapper">
            <LoadingState />
          </div>
        ) : (
          <pre>
            <code>{JSON.stringify(data, null, 2)}</code>
          </pre>
        )}
      </FlexColumn>
    </FlexColumn>
  );
}
