import type { PropertyFinancialReportEntity } from '@/types';
import { formatCop, type CurrencyRate } from '@/common/utils/currency';
import type { FormattedAmount, UseCurrencyValue } from '@/providers/CurrencyProvider';

/**
 * The rate a report's own `_usd` columns were computed with, as a `CurrencyRate`
 * - `null` for a row with no rate at all (a report that was never calculated).
 *
 * "The rate that produced a number is the rate that converts it": every figure
 * on a property page is either a stored COP/USD pair or a COP-only value that
 * was still computed alongside that rate, so nothing on this page should ever
 * be converted at today's live rate.
 */
export function reportCurrencyRate(
  report: Pick<PropertyFinancialReportEntity, 'exchange_rate' | 'calculated_at'>,
): CurrencyRate | null {
  if (report.exchange_rate == null) {
    return null;
  }

  return {
    rate: report.exchange_rate,
    rateAsOf: report.calculated_at ?? new Date().toISOString(),
    rateSource: 'report',
  };
}

/**
 * Formats a report-scoped COP figure through `reportCurrencyRate`, never
 * today's live rate. Falls back to a bare COP string when the report has no
 * rate at all, rather than forcing every caller through a null check before it
 * can call `useCurrency`'s formatters (which require a non-null rate by type).
 *
 * Pass `amountUsd` when the row stores a real sibling column (`formatStoredPair`
 * does no arithmetic); omit it for a COP-only column, which is derived instead
 * (`formatFromCop`).
 */
export function formatReportAmount(
  currency: Pick<UseCurrencyValue, 'formatFromCop' | 'formatStoredPair'>,
  rate: CurrencyRate | null,
  amountCop: number | null | undefined,
  amountUsd?: number | null,
): FormattedAmount {
  if (rate == null) {
    return { text: formatCop(amountCop), provenance: null, isUnavailable: false };
  }

  return amountUsd !== undefined
    ? currency.formatStoredPair(amountCop, amountUsd, rate)
    : currency.formatFromCop(amountCop, rate);
}
