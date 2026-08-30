import { Card, CardContent } from '@mui/material';
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet';

import type { MarketWithFinancialReportEntity } from '@/types';

import './styles.scss';

/** Roughly centres mainland Colombia. */
const COLOMBIA_CENTER: [number, number] = [4.5, -74.0];
const COLOMBIA_ZOOM = 6;

export function ColombiaMap({
  markets,
  onSelectMarket,
}: {
  markets: readonly MarketWithFinancialReportEntity[];
  /** Called with the market's `id` when its marker is clicked. */
  onSelectMarket: (marketId: string) => void;
}) {
  const markersWithCentroid = markets.filter(
    (market): market is MarketWithFinancialReportEntity & {
      latitude: number;
      longitude: number;
    } => market.latitude != null && market.longitude != null,
  );

  return (
    <Card className="colombia-map">
      <CardContent>
        <MapContainer
          id="colombia-map"
          center={COLOMBIA_CENTER}
          zoom={COLOMBIA_ZOOM}
          scrollWheelZoom={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {markersWithCentroid.map((market) => (
            <Marker
              key={market.id}
              position={[market.latitude, market.longitude]}
              eventHandlers={{
                click: () => {
                  onSelectMarket(market.id);
                },
              }}
            >
              <Popup>{market.locality}</Popup>
            </Marker>
          ))}
        </MapContainer>
      </CardContent>
    </Card>
  );
}
