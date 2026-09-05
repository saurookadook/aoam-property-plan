import { TextField } from '@mui/material';

import { FlexColumn, FlexRow } from '@/layouts';
import type { ManualEntryValues } from '../../utils';
import { PropertyLocationPicker } from '../PropertyLocationPicker';

import './styles.scss';

/**
 * The nine `MANUAL_FIELDS`, plus the optional and override fields the backend
 * accepts alongside them, as a single unit. `notes` only appears here, not on
 * the primary scrape path - `services/finca_raiz.py` writes JSON into that
 * column, and a scraped property's notes textarea would overwrite it.
 */
export function ManualEntryPanel({
  onChange,
  values,
}: {
  onChange: (values: ManualEntryValues) => void;
  values: ManualEntryValues;
}) {
  function setField<K extends keyof ManualEntryValues>(
    field: K,
    value: ManualEntryValues[K],
  ) {
    onChange({ ...values, [field]: value });
  }

  return (
    <FlexColumn className="manual-entry-panel">
      <FlexRow className="manual-entry-panel__row">
        <TextField
          label="Address"
          value={values.address}
          onChange={(event) => setField('address', event.target.value)}
        />
        <TextField
          label="Neighborhood"
          value={values.neighborhood}
          onChange={(event) => setField('neighborhood', event.target.value)}
        />
      </FlexRow>

      <FlexRow className="manual-entry-panel__row">
        <TextField
          label="City"
          value={values.city}
          onChange={(event) => setField('city', event.target.value)}
        />
        <TextField
          label="State"
          value={values.state}
          onChange={(event) => setField('state', event.target.value)}
        />
        <TextField
          label="Country"
          value={values.country}
          onChange={(event) => setField('country', event.target.value)}
        />
        <TextField
          label="Postal code"
          value={values.postal_code}
          onChange={(event) => setField('postal_code', event.target.value)}
        />
      </FlexRow>

      <FlexRow className="manual-entry-panel__row">
        <TextField
          label="Property type"
          value={values.property_type}
          onChange={(event) => setField('property_type', event.target.value)}
        />
        <TextField
          label="Bedrooms"
          type="number"
          value={values.bedrooms}
          onChange={(event) => setField('bedrooms', event.target.value)}
        />
        <TextField
          label="Purchase price (COP)"
          type="number"
          value={values.purchase_price_cop}
          onChange={(event) => setField('purchase_price_cop', event.target.value)}
        />
        <TextField
          label="Status"
          value={values.status}
          onChange={(event) => setField('status', event.target.value)}
        />
      </FlexRow>

      <FlexRow className="manual-entry-panel__row">
        <TextField
          label="Name"
          value={values.name}
          onChange={(event) => setField('name', event.target.value)}
        />
        <TextField
          label="Description"
          value={values.description}
          onChange={(event) => setField('description', event.target.value)}
        />
        <TextField
          label="Notes"
          value={values.notes}
          onChange={(event) => setField('notes', event.target.value)}
        />
      </FlexRow>

      <PropertyLocationPicker
        latitude={values.latitude}
        longitude={values.longitude}
        onPick={(latitude, longitude) => onChange({ ...values, latitude, longitude })}
      />
    </FlexColumn>
  );
}
