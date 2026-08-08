import classNames from 'classnames';
import useEmblaCarousel from 'embla-carousel-react';
import { Card, CardContent, CardHeader, Typography } from '@mui/material';

import type { HighestEarningListingEntity, NewestListingEntity } from '@/types';
import { CarouselControls } from './CarouselControls';

import './styles.scss';

export function ListingsCarousel({
  className,
  listingsItems,
}: {
  className?: string;
  listingsItems: Array<HighestEarningListingEntity | NewestListingEntity>;
}) {
  const [emblaRef, emblaApi] = useEmblaCarousel({ axis: 'y', loop: false });

  return (
    <div className={classNames('listings-carousel', className)}>
      <div className="embla__viewport" ref={emblaRef}>
        <div className="embla__container">
          {listingsItems.map((listing) => (
            <Card className="embla__slide" key={listing.id}>
              <CardHeader className="embla__slide__header">
                <Typography variant="h6" component="h3">
                  {listing.name}
                </Typography>
              </CardHeader>

              <CardContent className="embla__slide__content">
                <img
                  className="embla__slide__image"
                  src={listing.cover_photo_url}
                  alt={listing.name}
                />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {emblaApi != null && (
        <CarouselControls
          emblaApi={emblaApi} // force formatting
          totalListings={listingsItems.length}
        />
      )}
    </div>
  );
}
