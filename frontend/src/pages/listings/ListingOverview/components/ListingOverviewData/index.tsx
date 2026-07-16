import { Link as RouterLink } from 'react-router';
import { Masonry } from '@mui/lab';
import {
  Card,
  CardActions,
  CardContent,
  Divider,
  Paper,
  Typography,
} from '@mui/material';

import type { ListingEntity } from '@/types';
import { FlexColumn } from '@/layouts';

import './styles.scss';

export function ListingOverviewData({ listing }: { listing: ListingEntity }) {
  return (
    <FlexColumn className="listing-overview-data">
      <Card key={listing.id} className="listing-overview-data__data-item">
        <CardContent>
          <Typography variant="h2">{listing?.name ?? 'Name missing 🤷‍♂️'}</Typography>

          <Typography
            className="listing-overview-data__data-item__details-wrapper"
            variant="body2"
          >
            <Typography
              className="listing-overview-data__data-item__description"
              component="span"
            >
              {listing?.description ?? 'No description 🤷‍♂️'}
            </Typography>
          </Typography>
        </CardContent>
      </Card>
    </FlexColumn>
  );
}
