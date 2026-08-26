import { useLoaderData, type LoaderFunctionArgs } from 'react-router';
import { QueryClient, queryOptions, useSuspenseQuery } from '@tanstack/react-query';

import type { ListingEntity, MarketEntity } from '@/types';
import { LoadingState, Toast } from '@/common/components';
import { API_SERVER_DOMAIN } from '@/constants';
import { FlexColumn } from '@/layouts';
import { fetchy, unwrapEnvelope } from '@/utils';
import { MarketOverviewData } from './components';

import './styles.scss';

export const marketOverviewQuery = (marketId: string) =>
  queryOptions({
    queryKey: ['marketOverview', marketId],
    queryFn: async () => {
      const marketOverview = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/markets/${marketId}`) // force formatting
        .then(
          unwrapEnvelope<{
            listings: ListingEntity[];
            market: MarketEntity;
          }>,
        );

      return { marketOverview };
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
    <FlexColumn className="market-overview" id="market-overview">
      <FlexColumn className="market-overview__wrapper">
        {isFetching ? (
          <div className="loading-state__wrapper">
            <LoadingState />
          </div>
        ) : (
          <MarketOverviewData
            listings={data?.marketOverview?.listings ?? []}
            market={data?.marketOverview?.market ?? ({} as MarketEntity)}
          />
        )}
      </FlexColumn>

      {!isFetching && error != null && (
        <Toast
          error={error}
          fallbackErrorMessage="An unknown error occurred while fetching market overview data."
          status={status}
        />
      )}
    </FlexColumn>
  );
}
