import { useQuery } from '@tanstack/react-query';

import type { MarketEntity } from '@/types/markets';
import { LoadingState } from '@/common/components';
import { API_SERVER_DOMAIN } from '@/constants';
import { FlexColumn } from '@/layouts';
import { fetchy } from '@/utils';

import './styles.scss';

function useMarketsListQuery() {
  return useQuery({
    queryKey: ['marketsList'],
    queryFn: async () => {
      const marketsListResponse = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/markets`) // force formatting
        .then((res) => res.json());

      return { marketsList: marketsListResponse.data as MarketEntity[] };
    },
  });
}

export function MarketsList() {
  const { data, error, isFetching, status } = useMarketsListQuery();

  return (
    <FlexColumn id="markets-list">
      <h2>{`💰 Markets List 💰`}</h2>

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
