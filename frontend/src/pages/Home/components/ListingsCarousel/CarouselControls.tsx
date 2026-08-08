import type { EmblaAPI } from '@/types';
import { useCarouselEvents } from '@/common/utils/hooks';
import { NextButton, PrevButton } from './ArrowButtons';

export function CarouselControls({
  emblaApi,
  totalListings,
}: {
  emblaApi: EmblaAPI;
  totalListings: number;
}) {
  const {
    onNextButtonClick,
    onPrevButtonClick,
    nextBtnDisabled,
    prevBtnDisabled,
    selectedIndex,
  } = useCarouselEvents(emblaApi);

  return (
    <div className="embla__controls">
      <div className="embla__buttons">
        <PrevButton disabled={prevBtnDisabled} onClick={onPrevButtonClick} />
        <NextButton disabled={nextBtnDisabled} onClick={onNextButtonClick} />
      </div>

      <div className="embla__listings-counter">
        {emblaApi.scrollSnapList().length > 0 && (
          <span>{`${selectedIndex + 1} / ${totalListings}`}</span>
        )}
      </div>
    </div>
  );
}
