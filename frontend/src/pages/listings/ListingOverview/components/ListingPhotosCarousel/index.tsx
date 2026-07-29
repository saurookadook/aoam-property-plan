import classNames from 'classnames';
import useEmblaCarousel from 'embla-carousel-react';

import type { ListingEntity } from '@/types';
import { CarouselControls } from './CarouselControls';

import './styles.scss';

export function ListingPhotosCarousel({
  className,
  listing,
}: {
  className?: string;
  listing: ListingEntity;
}) {
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: false });

  return (
    <div className={classNames('embla', className)}>
      <div className="embla__viewport" ref={emblaRef}>
        <div className="embla__container">
          {listing.photo_urls.map((url, index) => (
            <div key={index} className="embla__slide">
              {/* <div className="embla__slide__number">
              <span>{index + 1}</span>
            </div> */}
              <img
                className="embla__slide__image"
                src={url}
                alt={`Listing photo ${index + 1}`}
              />
            </div>
          ))}
        </div>
      </div>

      {emblaApi != null && (
        <CarouselControls
          emblaApi={emblaApi} // force formatting
          totalPhotos={listing.photo_urls.length}
        />
      )}
    </div>
  );
}
