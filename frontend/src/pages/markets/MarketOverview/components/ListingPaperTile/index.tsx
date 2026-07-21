import { useState } from 'react';
import { Link as RouterLink } from 'react-router';
import classNames from 'classnames';
import { Paper, Skeleton, Typography } from '@mui/material';

import type { ListingEntity } from '@/types';
import { SmartImage } from '@/common/components';

import './styles.scss';

export function ListingPaperTile({ listing }: { listing: ListingEntity }) {
  return (
    <Paper className="listing-paper-tile">
      <RouterLink
        to={`/listings/${listing.id}`} // force formatting
        className="listing-paper-tile__link"
      >
        <Typography
          component="span" // force formatting
          className="listing-paper-tile__label"
        >
          {`${listing.name ?? listing.id} (${listing.property_type})`}
        </Typography>

        <SmartImage
          alt={`${listing.property_type} in ${listing.location}`}
          className="listing-paper-tile__image"
          src={listing.cover_photo_url}
        />
      </RouterLink>
    </Paper>
  );
}
