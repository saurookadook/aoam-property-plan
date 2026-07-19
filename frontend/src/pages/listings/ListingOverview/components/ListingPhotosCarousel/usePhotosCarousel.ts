import { useCallback, useEffect, useState } from 'react';

import type { EmblaAPI } from '@/types';

export const usePhotosCarousel = (emblaApi: EmblaAPI) => {
  const [prevBtnDisabled, setPrevBtnDisabled] = useState<boolean>(true);
  const [nextBtnDisabled, setNextBtnDisabled] = useState<boolean>(true);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [scrollSnaps, setScrollSnaps] = useState<number[]>([]);

  const onPrevButtonClick = useCallback(() => {
    if (emblaApi == null) return;
    emblaApi.scrollPrev();
    setScrollSnaps(emblaApi.scrollSnapList());
  }, [emblaApi]);

  const onNextButtonClick = useCallback(() => {
    if (emblaApi == null) return;
    emblaApi.scrollNext();
    setScrollSnaps(emblaApi.scrollSnapList());
  }, [emblaApi]);

  const onInit = useCallback((emblaApi: EmblaAPI) => {
    setScrollSnaps(emblaApi.scrollSnapList());
  }, []);

  const onSelect = useCallback((emblaApi: EmblaAPI) => {
    setPrevBtnDisabled(!emblaApi.canScrollPrev());
    setNextBtnDisabled(!emblaApi.canScrollNext());
    setSelectedIndex(emblaApi.selectedScrollSnap());
  }, []);

  useEffect(() => {
    if (emblaApi == null) return;

    // onInit(emblaApi);
    // onSelect(emblaApi);

    emblaApi.on('reInit', onInit);
    emblaApi.on('reInit', onSelect);
    emblaApi.on('select', onSelect);
  }, [emblaApi, onInit, onSelect]);

  return {
    onNextButtonClick,
    onPrevButtonClick,
    nextBtnDisabled,
    prevBtnDisabled,
    selectedIndex,
    scrollSnaps,
  };
};
