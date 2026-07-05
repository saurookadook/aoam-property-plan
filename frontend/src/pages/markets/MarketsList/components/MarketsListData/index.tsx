import { Card, Text } from '@chakra-ui/react';

import type { MarketEntity } from '@/types';
import { FlexRow } from '@/layouts';

import './styles.scss';

export function MarketsListData({
  marketsListData,
}: {
  marketsListData: MarketEntity[];
}) {
  return (
    <FlexRow className="markets-list-data">
      {marketsListData.map((market) => {
        return (
          <Card.Root key={market.locality}>
            <Card.Header>{market.locality}</Card.Header>

            <Card.Body>
              {market.district != null && <Text>District: {market.district}</Text>}
              <Text>Region: {market.region}</Text>
              <Text>Country: {market.country}</Text>
            </Card.Body>

            <Card.Footer>
              <details>
                <summary>Raw Data</summary>

                <pre>
                  <code>{JSON.stringify(market, null, 2)}</code>
                </pre>
              </details>
            </Card.Footer>
          </Card.Root>
        );
      })}
    </FlexRow>
  );
}
