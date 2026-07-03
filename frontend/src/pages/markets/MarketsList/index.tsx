import { useQuery } from '@tanstack/react-query';

import type { MarketEntity } from '@/types/markets';
import { LoadingState } from '@/common/components';
import { FlexColumn } from '@/layouts';

import './styles.scss';

function useMarketsListQuery() {
  return useQuery({
    queryKey: ['marketsList'],
    queryFn: async () => {
      const marketsListResponse = await fetch('/api/markets').then((res) => res.json());

      return { marketsList: marketsListResponse.data as MarketEntity[] };
    },
  });
}

export function MarketsList() {
  const { data, error, isFetching, status } = useMarketsListQuery();

  return (
    <FlexColumn id="markets-list">
      <h2>{`📈 Markets List 📈`}</h2>

      <FlexColumn>
        {isFetching ? (
          <div className="loading-state__wrapper">
            <LoadingState />
          </div>
        ) : (
          <div className="markets-list__wrapper">
            {(data?.marketsList ?? []).map((market) => {
              return (
                <pre key={market.locality}>
                  <code>{JSON.stringify(market, null, 2)}</code>
                </pre>
              );
            })}
          </div>
        )}
      </FlexColumn>
    </FlexColumn>
  );
}
