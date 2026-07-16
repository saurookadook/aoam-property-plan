import { useLoaderData, type LoaderFunctionArgs } from 'react-router';
import { QueryClient, queryOptions, useSuspenseQuery } from '@tanstack/react-query';

import type { ListingEntity, MarketEntity } from '@/types';
import { LoadingState } from '@/common/components';
import { API_SERVER_DOMAIN } from '@/constants';
import { FlexColumn } from '@/layouts';
import { fetchy } from '@/utils';
import { ListingOverviewData } from './components';

import './styles.scss';

export const listingOverviewQuery = (listingId: string) =>
  queryOptions({
    queryKey: ['listingOverview', listingId],
    queryFn: async () => {
      const listingOverviewResponse = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/listings/${listingId}`) // force formatting
        .then((res) => res.json());

      return {
        listingOverview: listingOverviewResponse.data as ListingEntity,
      };
    },
  });

export const listingOverviewLoader =
  (_queryClient: QueryClient) =>
  async ({ params }: LoaderFunctionArgs) => {
    if (!params.listingId) {
      throw new Error("No 'listingId' param provided!");
    }

    await _queryClient.ensureQueryData(listingOverviewQuery(params.listingId));
    return { listingId: params.listingId };
  };

export function ListingOverview() {
  const { listingId } = useLoaderData() as Awaited<
    ReturnType<ReturnType<typeof listingOverviewLoader>>
  >;
  const { data, error, isFetching, status } = useSuspenseQuery(
    listingOverviewQuery(listingId),
  );

  return (
    <FlexColumn className="listing-overview" id="listing-overview">
      <FlexColumn className="listing-overview__wrapper">
        {isFetching ? (
          <div className="loading-state__wrapper">
            <LoadingState />
          </div>
        ) : (
          <ListingOverviewData
            listing={data?.listingOverview ?? ({} as ListingEntity)}
          />
        )}
      </FlexColumn>
    </FlexColumn>
  );
}
