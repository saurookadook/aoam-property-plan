import { Card, CardContent, Chip, Typography } from '@mui/material';

import type { PropertyEntity } from '@/types';
import { ExternalLink } from '@/common/components';
import { formatCop, type CurrencyRate } from '@/common/utils/currency';
import { FlexColumn, FlexRow } from '@/layouts';
import { useCurrency } from '@/providers';

import './styles.scss';

export function PropertyHeaderCard({
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
    <Card className="property-header-card">
      <CardContent>
        <FlexRow className="property-header-card__top">
          <FlexColumn className="property-header-card__title-block">
            <Typography variant="h2">{property.name ?? property.address}</Typography>
            <Typography component="span" variant="body2">
              {`${property.address}, ${property.neighborhood}, ${property.city}, ${property.state}`}
            </Typography>
          </FlexColumn>

          <Chip className="property-header-card__status" label={property.status} />
        </FlexRow>

        <FlexRow className="property-header-card__facts">
          <Typography component="span">{`${property.bedrooms} bed`}</Typography>
          {property.baths != null && (
            <Typography component="span">{`${property.baths} bath`}</Typography>
          )}
          {property.guests != null && (
            <Typography component="span">{`${property.guests} guests`}</Typography>
          )}
          <Typography component="span">{property.property_type}</Typography>
          <Typography component="span">{priceText}</Typography>
        </FlexRow>

        <ExternalLink href={property.source_url}>View original listing</ExternalLink>
      </CardContent>
    </Card>
  );
}
