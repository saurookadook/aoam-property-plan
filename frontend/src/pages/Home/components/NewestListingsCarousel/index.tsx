import { queryOptions, useSuspenseQuery } from '@tanstack/react-query';

import type { NewestListingEntity } from '@/types';
import { LoadingState, Toast } from '@/common/components';
import { API_SERVER_DOMAIN } from '@/constants';
import { FlexColumn } from '@/layouts';
import { fetchy } from '@/utils';

export const newestListingsCarouselQuery = () =>
  queryOptions({
    queryKey: ['newestListingsCarousel'],
    queryFn: async () => {
      const newestListingsResponse = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/home/listings/newest`) // force formatting
        .then((res) => res.json());

      return {
        newestListings: newestListingsResponse.data as NewestListingEntity[],
      };
    },
  });

export function NewestListingsCarousel() {
  const { data, error, isFetching, status } = useSuspenseQuery(
    newestListingsCarouselQuery(),
  );

  return (
    <FlexColumn>
      {isFetching ? (
        <div className="loading-state__wrapper">
          <LoadingState />
        </div>
      ) : (
        <pre>
          <code>{JSON.stringify(data, null, 2)}</code>
        </pre>
      )}

      {!isFetching && error != null && (
        <Toast
          alertSeverity={status} // force formatting
          error={error}
          status={status}
        />
      )}
    </FlexColumn>
  );
}
