import classNames from 'classnames';
import { Typography } from '@mui/material';

import type { ListingEntity } from '@/types';
import { FlexColumn, FlexRow } from '@/layouts';
import { ListingDetailsCard } from '../ListingDetailsCard';
import { ListingDescriptionCard } from '../ListingDescriptionCard';
import { ListingFinancialReportsTable } from '../ListingFinancialReportsTable';
import { ListingMapCard } from '../ListingMapCard';
import { ListingPhotosCarousel } from '../ListingPhotosCarousel';

import './styles.scss';

export function ListingOverviewData({ listing }: { listing: ListingEntity }) {
  return (
    <FlexColumn className="listing-overview-data">
      <Typography variant="h2">{listing.name ?? 'Name missing 🤷‍♂️'}</Typography>

      <FlexRow
        className={classNames('listing-overview-data__top-row', 'overview-data-row')}
      >
        <ListingPhotosCarousel
          className="listing-overview-data__photos-carousel"
          listing={listing}
        />

        <ListingDetailsCard listing={listing} />
      </FlexRow>

      <FlexRow
        className={classNames('listing-overview-data__middle-row', 'overview-data-row')}
      >
        <ListingDescriptionCard description={listing.description} />

        <ListingMapCard listing={listing} />
      </FlexRow>

      <FlexRow
        className={classNames('listing-overview-data__bottom-row', 'overview-data-row')}
      >
        <ListingFinancialReportsTable
          financialReports={listing.listing_financial_reports}
        />
      </FlexRow>
    </FlexColumn>
  );
}
