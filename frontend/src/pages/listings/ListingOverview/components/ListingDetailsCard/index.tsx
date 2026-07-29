import { useMemo } from 'react';
import classNames from 'classnames';
import { Card, CardContent, Typography } from '@mui/material';

import type { ListingEntity } from '@/types';
import { FlexColumn } from '@/layouts';

import './styles.scss';

export function ListingDetailsCard({ listing }: { listing: ListingEntity }) {
  const uniqueAmenities = useMemo(() => {
    return Array.from(new Set(listing.amenities));
  }, [listing.amenities]);

  return (
    <FlexColumn className="listing-overview-data__details">
      <Card className="listing-overview-data__data-item">
        <CardContent>
          <dl>
            <dt>Property Type</dt>
            <dd className="listing-overview-data__data-item__item-wrapper">
              <Typography
                component="span"
                className="listing-overview-data__data-item__property-type"
              >
                {listing.property_type}
              </Typography>
            </dd>

            <dt>Beds & Baths</dt>
            <dd className="listing-overview-data__data-item__item-wrapper">
              <Typography
                component="span"
                className="listing-overview-data__data-item__bedrooms"
              >
                {listing.bedrooms} Bedrooms
              </Typography>

              <Typography
                component="span"
                className="listing-overview-data__data-item__beds"
              >
                {listing.beds ?? 0} Beds
              </Typography>

              <Typography
                component="span"
                className="listing-overview-data__data-item__baths"
              >
                {listing.baths ?? 0} Baths
              </Typography>
            </dd>

            <dt>Amenities</dt>
            <dd
              className={classNames(
                'listing-overview-data__data-item__item-wrapper',
                'amenities-list',
              )}
            >
              {uniqueAmenities.length > 0 ? (
                uniqueAmenities.map((amenity) => {
                  return (
                    <Typography
                      key={amenity}
                      className="listing-overview-data__data-item__amenity"
                      variant="body2"
                    >
                      {amenity}
                    </Typography>
                  );
                })
              ) : (
                <Typography
                  className="listing-overview-data__data-item__no-amenities"
                  variant="body2"
                >
                  No amenities listed 😕
                </Typography>
              )}
            </dd>
          </dl>
        </CardContent>
      </Card>
    </FlexColumn>
  );
}
