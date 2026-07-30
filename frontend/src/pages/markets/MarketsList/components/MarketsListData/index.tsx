import { Link as RouterLink } from 'react-router';
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
    <FlexRow id="markets-list-data" className="markets-list-data">
      {marketsListData.map((market) => {
        return (
          <Card key={market.id} className="markets-list-data__data-item">
            <CardContent>
              <Typography variant="h3">
                <RouterLink to={`/markets/${market.id}`}>{market.locality}</RouterLink>
              </Typography>

              <Typography
                className="markets-list-data__data-item__details-wrapper"
                variant="body2"
              >
                {market.district != null && (
                  <Typography component="span">District: {market.district}</Typography>
                )}
                <Typography component="span">Region: {market.region}</Typography>
                <Typography component="span">Country: {market.country}</Typography>
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
