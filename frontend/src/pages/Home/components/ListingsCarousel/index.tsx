import classNames from 'classnames';
import useEmblaCarousel from 'embla-carousel-react';

import type { HighestEarningListingEntity, NewestListingEntity } from '@/types';
import { CarouselControls } from './CarouselControls';

export function ListingsCarousel({
  listingsItems,
}: {
  listingsItems: Array<HighestEarningListingEntity | NewestListingEntity>;
}) {
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: false });

  return (
    <div className={classNames('embla', 'newest-listings-carousel')}>
      <div className="embla__viewport" ref={emblaRef}>
        <div className="embla__container">
          {listingsItems.map((listing) => (
            <div className="embla__slide" key={listing.id}>
              <img src={listing.cover_photo_url} alt={listing.name} />
            </div>
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
