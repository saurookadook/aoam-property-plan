import type { EmblaAPI } from '@/types';
import { NextButton, PrevButton } from './ArrowButtons';
import { usePhotosCarousel } from './usePhotosCarousel';

export function CarouselControls({
  emblaApi,
  totalPhotos,
}: {
  emblaApi: EmblaAPI;
  totalPhotos: number;
}) {
  const {
    onNextButtonClick,
    onPrevButtonClick,
    nextBtnDisabled,
    prevBtnDisabled,
    selectedIndex,
  } = usePhotosCarousel(emblaApi);

  return (
    <div className="embla__controls">
      <div className="embla__buttons">
        <PrevButton disabled={prevBtnDisabled} onClick={onPrevButtonClick} />
        <NextButton disabled={nextBtnDisabled} onClick={onNextButtonClick} />
      </div>

      <div className="embla__photos-counter">
        {emblaApi.scrollSnapList().length > 0 && (
          <span>{`${selectedIndex + 1} / ${totalPhotos}`}</span>
        )}
      </div>
    </div>
  );
}
