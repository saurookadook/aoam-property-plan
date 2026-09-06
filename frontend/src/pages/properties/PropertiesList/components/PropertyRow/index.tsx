import { Link as RouterLink } from 'react-router';
import { Card, CardContent, Chip, Typography } from '@mui/material';

import type { PropertyEntity } from '@/types';
import { formatCop, type CurrencyRate } from '@/common/utils/currency';
import { useCurrency } from '@/providers';
import { FlexColumn, FlexRow } from '@/layouts';

import './styles.scss';

export function PropertyRow({
  property,
  rate,
}: {
  property: PropertyEntity;
  rate: CurrencyRate | null;
}) {
  const { formatFromCop } = useCurrency();

  const priceText =
    rate != null
      ? formatFromCop(property.purchase_price_cop, rate).text
      : formatCop(property.purchase_price_cop);

  return (
    <Card className="property-row">
      <CardContent>
        <FlexRow className="property-row__inner">
          <FlexColumn className="property-row__details">
            <Typography variant="h6" className="property-row__name">
              <RouterLink to={`/properties/${property.id}`}>
                {property.name ?? property.address}
              </RouterLink>
            </Typography>

            <Typography component="span" variant="body2">
              {`${property.neighborhood}, ${property.city} · ${property.bedrooms} bed`}
              {property.baths != null ? ` / ${property.baths} bath` : ''}
            </Typography>
          </FlexColumn>

          <FlexRow className="property-row__meta">
            <Chip label={property.status} size="small" />
            <Typography component="span" variant="body2">
              {priceText}
            </Typography>
          </FlexRow>
        </FlexRow>
      </CardContent>
    </Card>
  );
}
