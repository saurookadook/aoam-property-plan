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

      <FlexRow className="listing-overview-data__top-row">
        <ListingPhotosCarousel
          className="listing-overview-data__photos-carousel"
          listing={listing}
        />

        <ListingDetailsCard listing={listing} />
      </FlexRow>

      <FlexRow className="listing-overview-data__middle-row">
        <ListingDescriptionCard description={listing.description} />

        <ListingMapCard
          latitude={listing.latitude} // force formatting
          longitude={listing.longitude}
        />
      </FlexRow>

      <FlexRow className="listing-overview-data__bottom-row">
        <ListingFinancialReportsTable
          financialReports={listing.listing_financial_reports}
        />
      </FlexRow>
    </FlexColumn>
  );
}
