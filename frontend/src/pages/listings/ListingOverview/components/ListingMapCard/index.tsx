import classNames from 'classnames';
import { Card, CardContent } from '@mui/material';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';

import './styles.scss';

export function ListingMapCard({
  className,
  latitude,
  longitude,
  ...props
}: {
  className?: string;
  latitude: number;
  longitude: number;
}) {
  const latLngPosition: [number, number] = [latitude, longitude];

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
              A pretty CSS3 popup. <br /> Easily customizable.
            </Popup>
          </Marker>
        </MapContainer>
      </CardContent>
    </Card>
  );
}
