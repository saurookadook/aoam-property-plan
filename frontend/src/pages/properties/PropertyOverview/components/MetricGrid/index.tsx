import classNames from 'classnames';
import { Tooltip, Typography } from '@mui/material';

import type { PropertyAnalysisData } from '@/types';
import { cocReturnTone, paybackTone, type MetricTone } from '@/common/utils/metricThresholds';
import type { DataConfidenceLevel } from '@/common/utils/dataConfidence';
import { useCurrency } from '@/providers';
import { FlexColumn } from '@/layouts';
import { formatReportAmount, reportCurrencyRate } from '../../utils';

import './styles.scss';

function MetricTile({
  label,
  tone,
  value,
}: {
  label: string;
  tone?: MetricTone;
  value: string;
}) {
  return (
    <FlexColumn
      className={classNames('metric-grid__tile', tone != null && `metric-grid__tile--${tone}`)}
    >
      <Typography component="span" variant="caption">
        {label}
      </Typography>
      <Typography component="span" variant="h4">
        {value}
      </Typography>
    </FlexColumn>
  );
}

/**
 * The doc's 3x3 metric grid. CoC return and payback are the two tiles that get
 * a `tone` - and both fall back to `'unrated'` (a neutral tile, number still
 * shown) whenever `confidence` is `'low'` or `'unknown'`. Colour is a
 * recommendation, and you do not recommend off a single mismatched comp.
 */
export function MetricGrid({
  analysis,
  confidence,
}: {
  analysis: PropertyAnalysisData;
  confidence: DataConfidenceLevel;
}) {
  const currency = useCurrency();
  const { expenses, report } = analysis;
  const rate = reportCurrencyRate(report);

  const money = (amountCop: number | null | undefined, amountUsd?: number | null) =>
    formatReportAmount(currency, rate, amountCop, amountUsd).text;

  const cocTone = cocReturnTone(report.coc_return_percentage, confidence);
  const paybackToneValue = paybackTone(report.payback_years, confidence);

  return (
    <FlexColumn className="metric-grid">
      <div className="metric-grid__grid">
        <MetricTile label="Purchase price" value={money(report.purchase_price_cop)} />
        <MetricTile
          label="Annual revenue"
          value={money(report.annual_revenue_cop, report.annual_revenue_usd)}
        />
        <MetricTile
          label="Annual net income"
          value={money(report.annual_net_income_cop, report.annual_net_income_usd)}
        />
        <MetricTile
          label="Cash invested"
          value={money(report.cash_invested_cop, report.cash_invested_usd)}
        />
        <MetricTile label="Monthly expenses" value={money(expenses.total_cop)} />
        <MetricTile label="Monthly mortgage" value={money(report.monthly_mortgage_cop)} />

        <Tooltip
          title={
            cocTone === 'unrated'
              ? 'Not colour-coded - data confidence is too low to recommend off.'
              : ''
          }
        >
          <div>
            <MetricTile
              label="Cash-on-cash return"
              tone={cocTone}
              value={
                report.coc_return_percentage == null
                  ? '—'
                  : `${report.coc_return_percentage.toFixed(1)}%`
              }
            />
          </div>
        </Tooltip>

        <Tooltip
          title={
            paybackToneValue === 'unrated'
              ? 'Not colour-coded - data confidence is too low to recommend off.'
              : ''
          }
        >
          <div>
            <MetricTile
              label="Payback period"
              tone={paybackToneValue}
              value={report.payback_years == null ? '—' : `${report.payback_years.toFixed(1)} yr`}
            />
          </div>
        </Tooltip>

        <MetricTile
          label="AirROI occupancy"
          value={
            report.airroi_occupancy_rate == null
              ? '—'
              : `${(report.airroi_occupancy_rate * 100).toFixed(0)}%`
          }
        />
      </div>
    </FlexColumn>
  );
}
