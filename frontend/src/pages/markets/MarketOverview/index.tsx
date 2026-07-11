import { useLoaderData, type LoaderFunctionArgs } from 'react-router';
import { QueryClient, queryOptions, useSuspenseQuery } from '@tanstack/react-query';

import type { ListingEntity, MarketEntity } from '@/types';
import { LoadingState } from '@/common/components';
import { API_SERVER_DOMAIN } from '@/constants';
import { FlexColumn } from '@/layouts';
import { fetchy } from '@/utils';
import { MarketOverviewData } from './components';

import './styles.scss';

export const marketOverviewQuery = (marketId: string) =>
  queryOptions({
    queryKey: ['marketOverview', marketId],
    queryFn: async () => {
      const marketOverviewResponse = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/markets/${marketId}`) // force formatting
        .then((res) => res.json());

      return {
        marketOverview: marketOverviewResponse.data as {
          listings: ListingEntity[];
          market: MarketEntity;
        },
      };
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

  console.log({
    component: 'MarketOverview',
    data,
  });

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
    </FlexColumn>
  );
}
