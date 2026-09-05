import { QueryClient, useSuspenseQuery } from '@tanstack/react-query';
import { Link as RouterLink } from 'react-router';
import { Button, Typography } from '@mui/material';

import { LoadingState, Toast } from '@/common/components';
import { useExchangeRateQuery } from '@/common/hooks/useExchangeRateQuery';
import { FlexColumn, FlexRow } from '@/layouts';
import { propertiesListQuery } from '../queries';
import { PropertyRow } from './components';

import './styles.scss';

export const propertiesListLoader = (_queryClient: QueryClient) => async () => {
  await _queryClient.ensureQueryData(propertiesListQuery);
  return null;
};

export function PropertiesList() {
  const {
    data: propertiesData,
    error: propertiesError,
    isPending: isPropertiesPending,
    status: propertiesStatus,
  } = useSuspenseQuery(propertiesListQuery);
  const { data: exchangeRateData } = useExchangeRateQuery();

  const rate =
    exchangeRateData?.exchangeRate == null
      ? null
      : ({
          rate: exchangeRateData.exchangeRate.cop_per_usd,
          rateAsOf: exchangeRateData.exchangeRate.record_date,
          rateSource: 'live',
        } as const);

  const properties = propertiesData?.propertiesList ?? [];

  return (
    <FlexColumn id="properties-list" className="properties-list">
      <FlexRow className="properties-list__header">
        <h2>{`🏠 Properties 🏠`}</h2>
        <Button component={RouterLink} to="/properties/new" variant="contained">
          Add property
        </Button>
      </FlexRow>

      <FlexColumn className="properties-list__wrapper">
        {isPropertiesPending ? (
          <div className="loading-state__wrapper">
            <LoadingState />
          </div>
        ) : properties.length === 0 ? (
          <Typography className="properties-list__empty-state" variant="body1">
            No properties yet - add your first candidate.
          </Typography>
        ) : (
          <FlexColumn className="properties-list__rows">
            {properties.map((property) => (
              <PropertyRow key={property.id} property={property} rate={rate} />
            ))}
          </FlexColumn>
        )}
      </FlexColumn>

      {!isPropertiesPending && propertiesError != null && (
        <Toast
          error={propertiesError}
          fallbackErrorMessage="An unknown error occurred while fetching the properties list."
          status={propertiesStatus}
        />
      )}
    </FlexColumn>
  );
}
