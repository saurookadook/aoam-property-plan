import { QueryClient, queryOptions, useSuspenseQuery } from '@tanstack/react-query';

import type { MarketWithFinancialReportEntity } from '@/types';
import { LoadingState, Toast } from '@/common/components';
import { API_SERVER_DOMAIN } from '@/constants';
import { HOUR_STALE_TIME, useExchangeRateQuery } from '@/common/hooks/useExchangeRateQuery';
import { FlexColumn } from '@/layouts';
import { fetchy, unwrapEnvelope } from '@/utils';
import { propertiesListQuery } from '@/pages/properties/queries';
import { MarketsListData } from './components';

import './styles.scss';

export const marketsListQuery = queryOptions({
  queryKey: ['marketsList'],
  queryFn: async () => {
    const marketsList = await fetchy
      .get(`${API_SERVER_DOMAIN}/api/markets`) // force formatting
      .then(unwrapEnvelope<MarketWithFinancialReportEntity[]>);

    return { marketsList };
  },
  staleTime: HOUR_STALE_TIME,
});

export const marketsListLoader = (_queryClient: QueryClient) => async () => {
  await Promise.all([
    _queryClient.ensureQueryData(marketsListQuery),
    _queryClient.ensureQueryData(propertiesListQuery),
  ]);

  return null;
};

export function MarketsList() {
  const {
    data: marketsData,
    error: marketsError,
    isPending: isMarketsPending,
    status: marketsStatus,
  } = useSuspenseQuery(marketsListQuery);
  const { data: propertiesData } = useSuspenseQuery(propertiesListQuery);
  const { data: exchangeRateData } = useExchangeRateQuery();

  const rate =
    exchangeRateData?.exchangeRate == null
      ? null
      : ({
          rate: exchangeRateData.exchangeRate.cop_per_usd,
          rateAsOf: exchangeRateData.exchangeRate.record_date,
          rateSource: 'live',
        } as const);

  return (
    <FlexColumn id="markets-list" className="markets-list">
      <h2>{`💰 Markets List 💰`}</h2>

      <FlexColumn className="markets-list__wrapper">
        {isMarketsPending ? (
          <div className="loading-state__wrapper">
            <LoadingState />
          </div>
        ) : (
          <MarketsListData
            marketsListData={marketsData?.marketsList ?? []}
            propertiesListData={propertiesData?.propertiesList ?? []}
            rate={rate}
          />
        )}
      </FlexColumn>

      {!isMarketsPending && marketsError != null && (
        <Toast
          error={marketsError}
          fallbackErrorMessage="An unknown error occurred while fetching the markets list."
          status={marketsStatus}
        />
      )}
    </FlexColumn>
  );
}
