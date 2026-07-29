import classNames from 'classnames';
import { Card, CardContent, type CardProps } from '@mui/material';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';

import type { ListingEntity } from '@/types';

import './styles.scss';

export function ListingMapCard({
  className,
  listing,
  ...props
}: {
  className?: string;
  listing: ListingEntity;
} & CardProps) {
  const latLngPosition: [number, number] = [listing.latitude, listing.longitude];

  return (
    <Card
      className={classNames('listing-overview-data__map', 'map-card', className)}
      {...props}
    >
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
              {`${listing.name} (${listing.property_type})`}
              <br />
              {`Lat: ${listing.latitude}, Long: ${listing.longitude}`}
            </Popup>
          </Marker>
        </MapContainer>
      </CardContent>
    </Card>
  );
}
