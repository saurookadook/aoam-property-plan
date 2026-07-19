import { useMemo } from 'react';
import { Link as RouterLink } from 'react-router';
import { Card, CardContent, Divider, Paper, Typography } from '@mui/material';

import type { ListingEntity } from '@/types';
import { FlexColumn, FlexRow } from '@/layouts';
import { ListingDescriptionCard } from '../ListingDescriptionCard';
import { ListingMapCard } from '../ListingMapCard';
import { ListingPhotosCarousel } from '../ListingPhotosCarousel';

import './styles.scss';

export function ListingOverviewData({ listing }: { listing: ListingEntity }) {
  const uniqueAmenities = useMemo(() => {
    return Array.from(new Set(listing.amenities));
  }, [listing.amenities]);

  return (
    <FlexColumn className="listing-overview-data">
      <Typography variant="h2">{listing.name ?? 'Name missing 🤷‍♂️'}</Typography>

      <FlexRow>
        <ListingPhotosCarousel
          className="listing-overview-data__photos-carousel"
          listing={listing}
        />

        <FlexColumn className="listing-overview-data__details">
          <Card className="listing-overview-data__data-item">
            <CardContent>
              <FlexRow style={{ gap: '1.5rem' }}>
                <Typography className="listing-overview-data__data-item__beds">
                  {listing.beds ?? 0} Beds
                </Typography>
                <Typography className="listing-overview-data__data-item__baths">
                  {listing.baths ?? 0} Baths
                </Typography>
              </FlexRow>

              {uniqueAmenities.map((amenity) => {
                return (
                  <Typography
                    key={amenity}
                    className="listing-overview-data__data-item__amenity"
                    variant="body2"
                  >
                    {amenity}
                  </Typography>
                );
              })}
            </CardContent>
          </Card>
        </FlexColumn>
      </FlexRow>

      <FlexRow className="listing-overview-data__middle-row">
        <ListingDescriptionCard description={listing.description} />

        <ListingMapCard
          latitude={listing.latitude} // force formatting
          longitude={listing.longitude}
        />
      </FlexRow>
    </FlexColumn>
  );
}
