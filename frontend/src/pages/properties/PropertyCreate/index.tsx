import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router';
import { ChevronDown } from 'lucide-react';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Button,
  TextField,
  Typography,
} from '@mui/material';

import { Toast } from '@/common/components';
import { FlexColumn } from '@/layouts';
import { useCreatePropertyMutation } from '../queries';
import { ManualEntryPanel } from './components';
import {
  buildManualCreateRequest,
  EMPTY_MANUAL_ENTRY_VALUES,
  isManualEntryComplete,
} from './utils';

import './styles.scss';

/**
 * `/properties/new` - a URL-first form with a disclosure into manual entry.
 *
 * The all-or-nothing manual validator makes a single-field form worse than it
 * looks: `MANUAL_FIELDS` includes `latitude`/`longitude`, and this codebase has
 * no geocoder, so the map picker inside `ManualEntryPanel` is what makes those
 * two fields fillable at all. `source_url` is required either way - the
 * backend uses it to prevent duplicates - so it stays outside the disclosure
 * and is relabelled once manual entry is open.
 */
export function PropertyCreate() {
  const navigate = useNavigate();
  const createMutation = useCreatePropertyMutation();

  const [sourceUrl, setSourceUrl] = useState('');
  const [isManualEntry, setIsManualEntry] = useState(false);
  const [manualValues, setManualValues] = useState(EMPTY_MANUAL_ENTRY_VALUES);

  const canSubmitScrape = sourceUrl.trim() !== '' && !isManualEntry;
  const canSubmitManual =
    isManualEntry && sourceUrl.trim() !== '' && isManualEntryComplete(manualValues);
  const canSubmit =
    (canSubmitScrape || canSubmitManual) && !createMutation.isPending;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!canSubmit) {
      return;
    }

    const body = isManualEntry
      ? buildManualCreateRequest(sourceUrl, manualValues)
      : { source_url: sourceUrl };

    const property = await createMutation.mutateAsync(body);
    void navigate(`/properties/${property.id}`);
  }

  return (
    <FlexColumn id="property-create" className="property-create">
      <h2>{`🏠 Add a Property 🏠`}</h2>

      <form className="property-create__form" onSubmit={handleSubmit}>
        <TextField
          label={
            isManualEntry
              ? 'Listing or reference URL (any unique URL; used to prevent duplicates)'
              : 'Finca Raiz URL'
          }
          className="property-create__source-url"
          fullWidth
          placeholder="https://www.fincaraiz.com.co/inmueble/..."
          value={sourceUrl}
          onChange={(event) => setSourceUrl(event.target.value)}
        />

        {!isManualEntry && (
          <Button
            className="property-create__submit"
            disabled={!canSubmit}
            type="submit"
            variant="contained"
          >
            Add property
          </Button>
        )}

        <Accordion
          className="property-create__manual-disclosure"
          expanded={isManualEntry}
          onChange={(_event, expanded) => setIsManualEntry(expanded)}
        >
          <AccordionSummary expandIcon={<ChevronDown />}>
            <Typography component="span">This isn't a Finca Raiz listing</Typography>
          </AccordionSummary>

          <AccordionDetails>
            <Typography className="property-create__manual-note" variant="body2">
              Re-submitting a URL already on file updates that property rather
              than creating a second one.
            </Typography>

            <ManualEntryPanel values={manualValues} onChange={setManualValues} />

            <Button
              className="property-create__submit"
              disabled={!canSubmit}
              type="submit"
              variant="contained"
            >
              Add property (manual entry)
            </Button>
          </AccordionDetails>
        </Accordion>
      </form>

      {createMutation.isError && (
        <Toast
          error={createMutation.error}
          fallbackErrorMessage="Could not create the property."
          status="error"
        />
      )}
    </FlexColumn>
  );
}
