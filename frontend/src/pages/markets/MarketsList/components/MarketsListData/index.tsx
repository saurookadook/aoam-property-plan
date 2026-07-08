import { Card, CardActions, CardContent, Typography } from '@mui/material';

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
          <Card key={market.locality}>
            <CardContent>
              <Typography variant="h3">{market.locality}</Typography>

              <Typography variant="body2">
                {market.district != null && (
                  <Typography>District: {market.district}</Typography>
                )}
                <Typography>Region: {market.region}</Typography>
                <Typography>Country: {market.country}</Typography>
              </Typography>
            </CardContent>

            <CardActions>
              <details>
                <summary>Raw Data</summary>

                <pre>
                  <code>{JSON.stringify(market, null, 2)}</code>
                </pre>
              </details>
            </CardActions>
          </Card>
        );
      })}
    </FlexRow>
  );
}
