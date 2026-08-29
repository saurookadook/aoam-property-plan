import type { DataConfidenceLevel } from './dataConfidence';

export type MetricTone = 'good' | 'fair' | 'poor' | 'unrated';

/** Cash-on-cash return, in percent. */
export const COC_GOOD_PERCENTAGE = 8;
export const COC_FAIR_PERCENTAGE = 4;

/**
 * The colour a cash-on-cash return is rendered in.
 *
 * `'unrated'` whenever confidence is low, and it is the whole point of this
 * function. Colour is a recommendation; you do not recommend off n=1. A CoC
 * return shown green because AirROI's model - unchecked by any real
 * comparable - happened to clear 8% is the most dangerous pixel in this app, so
 * the number is still shown and the judgement is withheld.
 */
export function cocReturnTone(
  cocReturnPercentage: number | null | undefined,
  confidence: DataConfidenceLevel,
): MetricTone {
  if (
    cocReturnPercentage == null ||
    !Number.isFinite(cocReturnPercentage) ||
    confidence === 'low' ||
    confidence === 'unknown'
  ) {
    return 'unrated';
  }

  if (cocReturnPercentage >= COC_GOOD_PERCENTAGE) {
    return 'good';
  }

  if (cocReturnPercentage >= COC_FAIR_PERCENTAGE) {
    return 'fair';
  }

  return 'poor';
}

/** Years to recoup the cash invested. Fewer is better, so the bounds invert. */
export const PAYBACK_GOOD_YEARS = 12;
export const PAYBACK_FAIR_YEARS = 20;

export function paybackTone(
  paybackYears: number | null | undefined,
  confidence: DataConfidenceLevel,
): MetricTone {
  if (
    paybackYears == null ||
    !Number.isFinite(paybackYears) ||
    paybackYears <= 0 ||
    confidence === 'low' ||
    confidence === 'unknown'
  ) {
    return 'unrated';
  }

  if (paybackYears <= PAYBACK_GOOD_YEARS) {
    return 'good';
  }

  if (paybackYears <= PAYBACK_FAIR_YEARS) {
    return 'fair';
  }

  return 'poor';
}
