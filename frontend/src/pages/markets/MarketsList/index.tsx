import { QueryClient, queryOptions, useQuery, useSuspenseQuery } from '@tanstack/react-query';

import type { ExchangeRateData, MarketWithFinancialReportEntity, PropertyEntity } from '@/types';
import { LoadingState, Toast } from '@/common/components';
import { API_SERVER_DOMAIN } from '@/constants';
import { FlexColumn } from '@/layouts';
import { fetchy, unwrapEnvelope } from '@/utils';
import { MarketsListData } from './components';

import './styles.scss';

/** Step 10's hour-long stale time, shared by every query this page issues. */
const HOUR_STALE_TIME = 1000 * 60 * 60;

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

export const propertiesListQuery = queryOptions({
  queryKey: ['propertiesList'],
  queryFn: async () => {
    const propertiesList = await fetchy
      .get(`${API_SERVER_DOMAIN}/api/properties`) // force formatting
      .then(unwrapEnvelope<PropertyEntity[]>);

    return { propertiesList };
  },
  staleTime: HOUR_STALE_TIME,
});

/**
 * A `useQuery`, not a suspense query - deliberately. `adr_usd` /
 * `annual_revenue_usd` are always NULL on a market's financial report, so this
 * live rate is the only way a market card's currency toggle can work at all,
 * but its absence (a 503, or a cold cache) should degrade the cards to COP
 * rather than take down the whole markets list.
 */
export function useExchangeRateQuery() {
  return useQuery({
    queryKey: ['exchangeRate'],
    queryFn: async () => {
      const exchangeRate = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/exchange-rate`) // force formatting
        .then(unwrapEnvelope<ExchangeRateData>);

      return { exchangeRate };
    },
    staleTime: HOUR_STALE_TIME,
    retry: false,
  });
}

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
