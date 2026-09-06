import { Typography } from '@mui/material';

import type { PropertyFinancialReportEntity } from '@/types';
import { useCurrency } from '@/providers';
import { FlexColumn, FlexRow } from '@/layouts';
import { formatReportAmount, reportCurrencyRate } from '../../utils';

import './styles.scss';

const WINNER_LABEL: Record<string, string> = {
  airroi_p25: 'AirROI (25th percentile)',
  airroi_avg: 'AirROI (average)',
  comp_derived: 'Comparable listings',
  airroi_p25_thin_comps: 'AirROI (25th percentile) - thin comps',
  airroi_avg_thin_comps: 'AirROI (average) - thin comps',
};

/**
 * The p25/p50/p75/p90 spread as a horizontal range bar, with the figure this
 * report actually used marked on it. Step 6 measured p90 at +94% over the mean
 * - far more informative than a +-10% sensitivity sweep, and it is already on
 * the row.
 */
function RevenueSpreadBar({
  chosenCop,
  p25,
  p50,
  p75,
  p90,
}: {
  chosenCop: number | null;
  p25: number | null;
  p50: number | null;
  p75: number | null;
  p90: number | null;
}) {
  if (p25 == null || p90 == null || p90 <= p25) {
    return null;
  }

  const width = 300;
  const toX = (value: number) => ((value - p25) / (p90 - p25)) * width;

  return (
    <svg
      className="revenue-spread-bar"
      viewBox={`0 0 ${width} 24`}
      role="img"
      aria-label={`Revenue percentile spread: p25 to p90, ${chosenCop != null ? 'chosen figure marked' : 'no figure chosen'}`}
    >
      <line x1={0} x2={width} y1={12} y2={12} stroke="currentColor" strokeWidth={2} />

      {p50 != null && (
        <circle cx={toX(p50)} cy={12} r={3} fill="currentColor" opacity={0.5}>
          <title>{`p50: ${p50.toLocaleString()}`}</title>
        </circle>
      )}
      {p75 != null && (
        <circle cx={toX(p75)} cy={12} r={3} fill="currentColor" opacity={0.5}>
          <title>{`p75: ${p75.toLocaleString()}`}</title>
        </circle>
      )}

      {chosenCop != null && (
        <circle cx={toX(chosenCop)} cy={12} r={5} className="revenue-spread-bar__chosen">
          <title>{`Chosen figure: ${chosenCop.toLocaleString()}`}</title>
        </circle>
      )}
    </svg>
  );
}

export function RevenueComparisonRow({
  report,
}: {
  report: PropertyFinancialReportEntity;
}) {
  const currency = useCurrency();
  const rate = reportCurrencyRate(report);
  const money = (amountCop: number | null) => formatReportAmount(currency, rate, amountCop).text;

  return (
    <FlexColumn className="revenue-comparison-row">
      <Typography variant="h3">Revenue estimate</Typography>

      <FlexRow className="revenue-comparison-row__figures">
        <FlexColumn>
          <Typography component="span" variant="caption">
            AirROI direct
          </Typography>
          <Typography component="span">{money(report.airroi_revenue_cop)}</Typography>
        </FlexColumn>

        <FlexColumn>
          <Typography component="span" variant="caption">
            Comp-derived
          </Typography>
          <Typography component="span">{money(report.comp_derived_revenue_cop)}</Typography>
        </FlexColumn>

        <FlexColumn>
          <Typography component="span" variant="caption">
            Used in this analysis
          </Typography>
          <Typography component="span">
            {report.annual_revenue_source == null
              ? '—'
              : (WINNER_LABEL[report.annual_revenue_source] ?? report.annual_revenue_source)}
          </Typography>
        </FlexColumn>
      </FlexRow>

      <RevenueSpreadBar
        chosenCop={report.annual_revenue_cop}
        p25={report.airroi_revenue_p25_cop}
        p50={report.airroi_revenue_p50_cop}
        p75={report.airroi_revenue_p75_cop}
        p90={report.airroi_revenue_p90_cop}
      />
    </FlexColumn>
  );
}
