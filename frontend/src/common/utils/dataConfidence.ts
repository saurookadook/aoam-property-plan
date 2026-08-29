import type { AnnualRevenueSource } from '@/types';

export type DataConfidenceLevel = 'good' | 'fair' | 'low' | 'unknown';

export type DataConfidence = {
  level: DataConfidenceLevel;
  message: string;
};

/** Below this, a median over the surviving comps is not an estimate. */
export const GOOD_COMP_COUNT = 10;
export const FAIR_COMP_COUNT = 5;

const THIN_COMPS_SUFFIX = '_thin_comps';

/**
 * How much of a report's revenue figure is corroborated by real comparables.
 *
 * The `_thin_comps` sources are the dangerous case: AirROI's model produced a
 * number, and too few comparable listings survived reconciliation to check it.
 * For Calima that is a single comp - and it was a 5br/5.5ba/16-guest property
 * returned for a 2br query. `'low'` is what disables the metric colour coding;
 * see `cocReturnTone`.
 */
export function dataConfidence(
  source: AnnualRevenueSource | null | undefined,
  compCount: number | null | undefined,
): DataConfidence {
  const count = compCount ?? 0;

  if (source == null) {
    return {
      level: 'unknown',
      message: 'This property has not been analysed yet.',
    };
  }

  if (source.endsWith(THIN_COMPS_SUFFIX)) {
    return {
      level: 'low',
      message:
        `Low confidence — AirROI's model only, ` +
        `${count} comparable listing${count === 1 ? '' : 's'}.`,
    };
  }

  if (source !== 'comp_derived') {
    return {
      level: 'low',
      message: `Low confidence — AirROI's model only, ${count} comparable listings.`,
    };
  }

  if (count >= GOOD_COMP_COUNT) {
    return {
      level: 'good',
      message: `Good confidence — median of ${count} comparable listings.`,
    };
  }

  if (count >= FAIR_COMP_COUNT) {
    return {
      level: 'fair',
      message: `Fair confidence — median of ${count} comparable listings.`,
    };
  }

  return {
    level: 'low',
    message: `Low confidence — only ${count} comparable listing${count === 1 ? '' : 's'}.`,
  };
}
