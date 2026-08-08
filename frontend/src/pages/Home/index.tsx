import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { LoadingState } from '@/common/components';
import { FlexColumn } from '@/layouts';
import { TrendsRow } from './components';

import './styles.scss';

function useTestQuery() {
  return useQuery({
    queryKey: ['testQuery'],
    queryFn: async () => {
      const testData =
        JSON.parse(window.localStorage.getItem('testData') ?? 'null') ?? [];
      await new Promise((resolve) => setTimeout(resolve, 1000));
      return { testData };
    },
  });
}

export function Home() {
  const { data, error, isFetching, status } = useTestQuery();

  const [count, setCount] = useState(0);

  function handleCounterClick(
    event: React.MouseEvent<HTMLButtonElement>, // force formatting
  ) {
    const newCount = count + 1;
    setCount(newCount);
    data?.testData.push(newCount);
    window.localStorage.setItem('testData', JSON.stringify(data?.testData ?? []));
  }

  return (
    <FlexColumn id="home" className="home">
      <h2>{`🏡 Home 🏡`}</h2>

      <TrendsRow className="home__top-row" />

      <button // force formatting
        onClick={handleCounterClick}
      >
        count is {count}
      </button>

      <FlexColumn>
        {isFetching ? (
          <LoadingState />
        ) : (
          <pre>
            <code>{JSON.stringify(data?.testData ?? [], null, 2)}</code>
          </pre>
        )}
      </FlexColumn>
    </FlexColumn>
  );
}
