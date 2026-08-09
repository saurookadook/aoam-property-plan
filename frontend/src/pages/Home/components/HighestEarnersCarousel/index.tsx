import classNames from 'classnames';
import { queryOptions, useSuspenseQuery } from '@tanstack/react-query';

import type { HighestEarningListingEntity } from '@/types';
import { LoadingState, Toast } from '@/common/components';
import { API_SERVER_DOMAIN } from '@/constants';
import { FlexColumn } from '@/layouts';
import { fetchy } from '@/utils';
import { ListingsCarousel } from '../ListingsCarousel';

export const highestEarnersListingsCarouselQuery = () =>
  queryOptions({
    queryKey: ['highestEarnersListingsCarousel'],
    queryFn: async () => {
      const highestEarnersListingsResponse = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/home/listings/highest-earners`) // force formatting
        .then((res) => res.json());

      return {
        highestEarnersListings:
          highestEarnersListingsResponse.data as HighestEarningListingEntity[],
      };
    },
  });

export function HighestEarnersCarousel() {
  const { data, error, isFetching, status } = useSuspenseQuery(
    highestEarnersListingsCarouselQuery(),
  );

  return (
    <FlexColumn className={classNames('home-carousel')}>
      {isFetching ? (
        <div className="loading-state__wrapper">
          <LoadingState />
        </div>
      ) : (
        <ListingsCarousel
          carouselTitle="Highest Earners"
          listingsItems={data?.highestEarnersListings ?? []}
        />
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
