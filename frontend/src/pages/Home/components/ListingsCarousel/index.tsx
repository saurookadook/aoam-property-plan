import classNames from 'classnames';
import useEmblaCarousel from 'embla-carousel-react';
import { Typography } from '@mui/material';

import type { HighestEarningListingEntity, NewestListingEntity } from '@/types';
import { FlexColumn } from '@/layouts';
import { ListingCarouselCard } from '../ListingCarouselCard';
import { CarouselControls } from './CarouselControls';

import './styles.scss';

export function ListingsCarousel({
  carouselTitle,
  className,
  listingsItems,
}: {
  carouselTitle?: string;
  className?: string;
  listingsItems: Array<HighestEarningListingEntity | NewestListingEntity>;
}) {
  const [emblaRef, emblaApi] = useEmblaCarousel({ axis: 'y', loop: false });

  return (
    <FlexColumn className={classNames('listings-carousel', className)}>
      {carouselTitle != null && (
        <Typography component="h3" variant="h6">
          {carouselTitle}
        </Typography>
      )}

      <div className="listings-carousel__wrapper">
        <div className="embla__viewport" ref={emblaRef}>
          <div className="embla__container">
            {listingsItems.map((listing, index) => {
              console.log({
                className,
                index,
                listing,
              });

              return (
                <ListingCarouselCard
                  key={listing.id} // force formatting
                  listing={listing}
                />
              );
            })}
          </div>
        </div>

        {emblaApi != null && (
          <CarouselControls
            emblaApi={emblaApi} // force formatting
            totalListings={listingsItems.length}
          />
        )}
      </div>
    </FlexColumn>
  );
}
