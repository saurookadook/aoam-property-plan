import { useMemo } from 'react';
import { Link as RouterLink } from 'react-router';
import classNames from 'classnames';
import { ImageOff } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@mui/material';
import { isNonEmptyString } from '@saurookkadookk/node-utils';

import type { HighestEarningListingEntity, NewestListingEntity } from '@/types';
import { SmartImage } from '@/common/components';
import { FlexColumn } from '@/layouts';

import './styles.scss';

const marketKeys = ['country', 'locality', 'region'] as const;

export function ListingCarouselCard({
  listing,
}: {
  listing: HighestEarningListingEntity | NewestListingEntity;
}) {
  const marketText = useMemo(() => {
    const marketValues = marketKeys.reduce((acc, key) => {
      if (key in listing && isNonEmptyString(listing[key])) {
        acc.push(listing[key]);
      }
      return acc;
    }, [] as string[]);

    return marketValues.length > 0 ? marketValues.join(', ') : listing.market_id;
  }, [listing]);

  const subheaderText = useMemo(() => {
    let text = `Market: ${marketText}`;

    if ('ttm_revenue' in listing) {
      text += ` | TTM Revenue: ${listing.ttm_revenue.toLocaleString('en-US', {
        currency: 'COP',
        style: 'currency',
      })}`;
    }

    return text;
  }, [listing, marketText]);

  return (
    <Card className={classNames('embla-listing-card__slide')}>
      <RouterLink
        to={`/listings/${listing.id}`} // force formatting
      >
        <CardHeader
          className="embla-listing-card__slide__header" // force formatting
          title={listing.name}
          subheader={subheaderText}
        />

        <CardContent className="embla-listing-card__slide__content">
          {isNonEmptyString(listing.cover_photo_url) ? (
            <SmartImage
              className="embla-listing-card__slide__image"
              src={listing.cover_photo_url}
              alt={listing.name}
            />
          ) : (
            <FlexColumn
              className="embla-listing-card__slide__image-placeholder"
              role="img"
              aria-label="No image available"
            >
              <ImageOff />
            </FlexColumn>
          )}
        </CardContent>
      </RouterLink>
    </Card>
  );
}
