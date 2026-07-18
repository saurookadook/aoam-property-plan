import { Link as RouterLink } from 'react-router';
import classNames from 'classnames';
import DOMPurify from 'dompurify';
import { Masonry } from '@mui/lab';
import {
  Card,
  CardActions,
  CardContent,
  Divider,
  Paper,
  Typography,
} from '@mui/material';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';

import type { ListingEntity } from '@/types';
import { FlexColumn, FlexRow } from '@/layouts';

import './styles.scss';

export function ListingOverviewData({ listing }: { listing: ListingEntity }) {
  const latLngPosition: [number, number] = [
    listing?.latitude ?? 0,
    listing?.longitude ?? 0,
  ];

  return (
    <FlexColumn className="listing-overview-data">
      <Typography variant="h2">{listing?.name ?? 'Name missing 🤷‍♂️'}</Typography>

      <FlexRow className="listing-overview-data__top-row">
        <Card className="listing-overview-data__data-item">
          <CardContent>
            <Typography
              className="listing-overview-data__data-item__details-wrapper"
              variant="body2"
            >
              <Typography
                className="listing-overview-data__data-item__description"
                component="span"
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(
                    listing?.description ?? 'No description 🤷‍♂️',
                  ),
                }}
              />
            </Typography>
          </CardContent>
        </Card>

        <Card className={classNames('listing-overview-data__map', 'map-card')}>
          <CardContent>
            <MapContainer
              id="listing-overview-map"
              center={latLngPosition}
              zoom={13}
              scrollWheelZoom={false}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              <Marker position={latLngPosition}>
                <Popup>
                  A pretty CSS3 popup. <br /> Easily customizable.
                </Popup>
              </Marker>
            </MapContainer>
          </CardContent>
        </Card>
      </FlexRow>
    </FlexColumn>
  );
}
