import { FlexRow } from '@/layouts';

import { HighestEarnersCarousel } from '../HighestEarnersCarousel';
import { NewestListingsCarousel } from '../NewestListingsCarousel';

export function TrendsRow() {
  return (
    <FlexRow>
      <NewestListingsCarousel />

      <HighestEarnersCarousel />
    </FlexRow>
  );
}
