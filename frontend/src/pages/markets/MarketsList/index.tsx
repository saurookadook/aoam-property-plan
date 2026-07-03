import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { LoadingState } from '@/common/components';
import { FlexColumn } from '@/layouts';

import './styles.scss';

function useMarketsListQuery() {
  return useQuery({
    queryKey: ['marketsList'],
    queryFn: async () => {
      const marketsListResponse = await fetch('/api/markets').then((res) => res.json());

      return { marketsList: marketsListResponse.data };
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
          <pre>
            <code>{JSON.stringify(data?.marketsList ?? [], null, 2)}</code>
          </pre>
        )}
      </FlexColumn>
    </FlexColumn>
  );
}
