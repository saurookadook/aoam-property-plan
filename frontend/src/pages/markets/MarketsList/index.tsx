import { useQuery } from '@tanstack/react-query';

import type { MarketWithFinancialReportEntity } from '@/types';
import { LoadingState, Toast } from '@/common/components';
import { API_SERVER_DOMAIN } from '@/constants';
import { FlexColumn } from '@/layouts';
import { fetchy, unwrapEnvelope } from '@/utils';
import { MarketsListData } from './components';

import './styles.scss';

function useMarketsListQuery() {
  return useQuery({
    queryKey: ['marketsList'],
    queryFn: async () => {
      const marketsList = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/markets`) // force formatting
        .then(unwrapEnvelope<MarketWithFinancialReportEntity[]>);

      return { marketsList };
    },
  });
}

export function MarketsList() {
  const { data, error, isFetching, status } = useMarketsListQuery();

  return (
    <FlexColumn id="markets-list" className="markets-list">
      <h2>{`💰 Markets List 💰`}</h2>

      <FlexColumn className="markets-list__wrapper">
        {isFetching ? (
          <div className="loading-state__wrapper">
            <LoadingState />
          </div>
        ) : (
          <MarketsListData marketsListData={data?.marketsList ?? []} />
        )}
      </FlexColumn>

      {!isFetching && error != null && (
        <Toast
          error={error}
          fallbackErrorMessage="An unknown error occurred while fetching the markets list."
          status={status}
        />
      )}
    </FlexColumn>
  );
}
