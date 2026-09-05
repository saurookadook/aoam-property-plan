import { useState, type FormEvent } from 'react';
import { Button, Slider, TextField, Typography } from '@mui/material';

import type { PropertyAnalyzeRequest } from '@/types';
import { Toast } from '@/common/components';
import { FlexColumn, FlexRow } from '@/layouts';
import { useAnalyzePropertyMutation } from '../../../queries';

import './styles.scss';

type SliderKnob = {
  field: keyof PropertyAnalyzeRequest;
  label: string;
  max: number;
  min: number;
  step: number;
  unit: string;
};

const SLIDER_KNOBS: SliderKnob[] = [
  {
    field: 'down_payment_percentage',
    label: 'Down payment',
    min: 0,
    max: 100,
    step: 1,
    unit: '%',
  },
  {
    field: 'interest_rate_percentage',
    label: 'Interest rate',
    min: 0,
    max: 25,
    step: 0.5,
    unit: '%',
  },
  {
    field: 'loan_term_years',
    label: 'Loan term',
    min: 5,
    max: 30,
    step: 1,
    unit: ' yr',
  },
  {
    field: 'management_fee_percentage',
    label: 'Management fee',
    min: 0,
    max: 40,
    step: 1,
    unit: '%',
  },
  {
    field: 'maintenance_reserve_percentage',
    label: 'Maintenance reserve',
    min: 0,
    max: 5,
    step: 0.25,
    unit: '%',
  },
  {
    field: 'closing_costs_percentage',
    label: 'Closing costs',
    min: 0,
    max: 10,
    step: 0.25,
    unit: '%',
  },
  {
    field: 'predial_rate_percentage',
    label: 'Predial rate',
    min: 0,
    max: 3,
    step: 0.1,
    unit: '%',
  },
];

/**
 * The first `useMutation` in the repo. Seeded either from
 * `reportToScenarioOverrides(report)` for a re-analysis, or from
 * `DEFAULT_SCENARIO_OVERRIDES` for a property with no report yet - the caller
 * decides which, this component only renders and submits.
 *
 * `retry: false` plus a submit disabled while pending is load-bearing, not
 * cosmetic: `POST /analyze` inserts a **new row on every call**, so a
 * double-click writes two reports and spends two AirROI calls.
 */
export function AssumptionsPanel({
  initialOverrides,
  propertyId,
  submitLabel,
}: {
  initialOverrides: PropertyAnalyzeRequest;
  propertyId: string;
  submitLabel: string;
}) {
  const [overrides, setOverrides] = useState<PropertyAnalyzeRequest>(initialOverrides);
  const analyzeMutation = useAnalyzePropertyMutation(propertyId);

  function setField(field: keyof PropertyAnalyzeRequest, value: number) {
    setOverrides((previous) => ({ ...previous, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (analyzeMutation.isPending) {
      return;
    }

    await analyzeMutation.mutateAsync(overrides);
  }

  return (
    <FlexColumn className="assumptions-panel">
      <form className="assumptions-panel__analyse-form" onSubmit={handleSubmit}>
        <FlexRow className="assumptions-panel__knobs-and-amounts">
          <FlexColumn className="assumptions-panel__knobs-wrapper">
            {SLIDER_KNOBS.map((knob) => {
              const value = overrides[knob.field] ?? knob.min;

              return (
                <FlexColumn key={knob.field} className="assumptions-panel__knob">
                  <Typography component="span" variant="body2">
                    {`${knob.label}: ${value}${knob.unit}`}
                  </Typography>
                  <Slider
                    aria-label={knob.label}
                    max={knob.max}
                    min={knob.min}
                    step={knob.step}
                    value={value}
                    valueLabelDisplay="auto"
                    onChange={(_event, nextValue) => {
                      setField(knob.field, nextValue as number);
                    }}
                  />
                </FlexColumn>
              );
            })}
          </FlexColumn>

          <FlexColumn className="assumptions-panel__amounts">
            <TextField
              label="Purchase price (COP)"
              type="number"
              value={overrides.purchase_price_cop ?? ''}
              onChange={(event) =>
                setField('purchase_price_cop', Number(event.target.value))
              }
            />
            <TextField
              label="Assessed value (COP)"
              type="number"
              value={overrides.assessed_value_cop ?? ''}
              onChange={(event) =>
                setField('assessed_value_cop', Number(event.target.value))
              }
            />
            <TextField
              label="HOA, monthly (COP)"
              type="number"
              value={overrides.hoa_monthly_cop ?? ''}
              onChange={(event) =>
                setField('hoa_monthly_cop', Number(event.target.value))
              }
            />
            <TextField
              label="Renovation budget (COP)"
              type="number"
              value={overrides.renovation_budget_cop ?? ''}
              onChange={(event) =>
                setField('renovation_budget_cop', Number(event.target.value))
              }
            />
          </FlexColumn>
        </FlexRow>

        <Button disabled={analyzeMutation.isPending} type="submit" variant="contained">
          {submitLabel}
        </Button>
      </form>

      {analyzeMutation.isError && (
        <Toast
          error={analyzeMutation.error}
          fallbackErrorMessage="Could not analyse this property."
          status="error"
        />
      )}
    </FlexColumn>
  );
}
