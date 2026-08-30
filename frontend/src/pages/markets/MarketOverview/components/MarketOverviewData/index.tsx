import { Masonry } from '@mui/lab';
import { Card, CardContent, Divider, Typography } from '@mui/material';

import type { ListingEntity, MarketEntity } from '@/types';
import { FlexColumn } from '@/layouts';
import { ListingPaperTile } from '../ListingPaperTile';

import './styles.scss';

export function MarketOverviewData({
  listings,
  market,
}: {
  listings: ListingEntity[];
  market: MarketEntity;
}) {
  return (
    <FlexColumn className="market-overview-data">
      <Card key={market.locality} className="market-overview-data__data-item">
        <CardContent>
          <Typography variant="h2">{market.locality}</Typography>

          <Typography
            className="market-overview-data__data-item__details-wrapper"
            variant="body2"
          >
            {market.district != null && (
              <Typography
                className="market-overview-data__data-item__district"
                component="span"
              >
                District: {market.district}
              </Typography>
            )}
            <Typography
              className="market-overview-data__data-item__region"
              component="span"
            >
              Region: {market.region}
            </Typography>
            <Typography
              className="market-overview-data__data-item__country"
              component="span"
            >
              Country: {market.country}
            </Typography>
          </Typography>
        </CardContent>
      </Card>

      <Divider orientation="horizontal" flexItem />

      {listings.length > 0 ? (
        <ListingsMasonry listings={listings} />
      ) : (
        <FlexColumn className="market-overview-data__no-listings-wrapper">
          <Typography className="market-overview-data__no-listings" variant="body1">
            {`No listings found for this market. ☹️`}
          </Typography>
        </FlexColumn>
      )}
    </FlexColumn>
  );
}

function ListingsMasonry({ listings }: { listings: ListingEntity[] }) {
  return (
    <Masonry className="market-overview-data__masonry" columns={4} spacing={2}>
      {listings.map((listing) => {
        return (
          <ListingPaperTile
            key={listing.id} // force formatting
            listing={listing}
          />
        );
      })}
    </Masonry>
  );
}
