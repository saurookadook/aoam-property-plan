import { Card, CardContent, Typography } from '@mui/material';
import { MapContainer, Marker, TileLayer, useMapEvents } from 'react-leaflet';

import { FlexColumn } from '@/layouts';

import './styles.scss';

/** Roughly centres mainland Colombia - the same default `ColombiaMap` uses. */
const COLOMBIA_CENTER: [number, number] = [4.5, -74.0];
const COLOMBIA_ZOOM = 6;

function ClickToSetLocation({
  onPick,
}: {
  onPick: (latitude: number, longitude: number) => void;
}) {
  useMapEvents({
    click: (event) => {
      onPick(event.latlng.lat, event.latlng.lng);
    },
  });

  return null;
}

/**
 * The worst field on the manual-entry form turned into the easiest: click the
 * map, get `latitude`/`longitude`. Nobody types `4.5709, -74.2973` by hand, and
 * there is no geocoder in this codebase to derive it from an address.
 */
export function PropertyLocationPicker({
  latitude,
  longitude,
  onPick,
}: {
  latitude: number | null;
  longitude: number | null;
  onPick: (latitude: number, longitude: number) => void;
}) {
  const hasPosition = latitude != null && longitude != null;
  const center: [number, number] = hasPosition
    ? [latitude, longitude]
    : COLOMBIA_CENTER;

  return (
    <FlexColumn className="property-location-picker">
      <Typography component="span" variant="body2">
        {hasPosition
          ? `Lat: ${latitude.toFixed(5)}, Long: ${longitude.toFixed(5)}`
          : 'Click the map to set the property location.'}
      </Typography>

      <Card className="property-location-picker__map">
        <CardContent>
          <MapContainer
            id="property-location-picker-map"
            center={center}
            zoom={hasPosition ? 13 : COLOMBIA_ZOOM}
            scrollWheelZoom={false}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <ClickToSetLocation onPick={onPick} />

            {hasPosition && <Marker position={[latitude, longitude]} />}
          </MapContainer>
        </CardContent>
      </Card>
    </FlexColumn>
  );
}
