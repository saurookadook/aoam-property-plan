import { Alert, type AlertColor } from '@mui/material';

import type { AnnualRevenueSource } from '@/types';
import { dataConfidence, type DataConfidenceLevel } from '@/common/utils/dataConfidence';

const SEVERITY_BY_LEVEL: Record<DataConfidenceLevel, AlertColor> = {
  good: 'success',
  fair: 'info',
  low: 'warning',
  unknown: 'info',
};

/**
 * Above the metric grid, not a footnote - a CoC return rendered green off a
 * single mismatched comp is the most dangerous pixel in this app, so the
 * caveat has to be seen before the number that depends on it.
 */
export function DataConfidenceBanner({
  compCount,
  source,
}: {
  compCount: number | null | undefined;
  source: AnnualRevenueSource | null | undefined;
}) {
  const confidence = dataConfidence(source, compCount);

  return (
    <Alert
      className="data-confidence-banner"
      severity={SEVERITY_BY_LEVEL[confidence.level]}
      variant="outlined"
    >
      {confidence.message}
    </Alert>
  );
}
