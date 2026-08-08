import classNames from 'classnames';

import { FlexRow } from '@/layouts';
import { HighestEarnersCarousel } from '../HighestEarnersCarousel';
import { NewestListingsCarousel } from '../NewestListingsCarousel';

export function TrendsRow({ className }: { className?: string }) {
  return (
    <FlexRow id="trends-row" className={classNames(className, 'row')}>
      <NewestListingsCarousel />

      <HighestEarnersCarousel />
    </FlexRow>
  );
}
