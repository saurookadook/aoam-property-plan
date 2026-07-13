import { Link as RouterLink } from 'react-router';
import { Masonry } from '@mui/lab';
import {
  Card,
  CardActions,
  CardContent,
  Divider,
  Paper,
  Typography,
} from '@mui/material';

import type { ListingEntity, MarketEntity } from '@/types';
import { FlexColumn } from '@/layouts';

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

      <Masonry className="market-overview-data__masonry" columns={4} spacing={2}>
        {listings.map((listing) => {
          return (
            <div key={listing.id} className="market-overview-data__listing-tile">
              <Paper className="market-overview-data__listing-tile__paper">{`${listing.id} (${listing.property_type})`}</Paper>
              <img
                alt={`${listing.property_type} in ${listing.location}`}
                className="market-overview-data__listing-tile__image"
                srcSet={listing.cover_photo_url}
                src={listing.cover_photo_url}
                loading="lazy"
              />
            </div>
          );
        })}
      </Masonry>
    </FlexColumn>
  );
}
