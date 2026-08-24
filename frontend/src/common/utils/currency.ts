/**
 * COP/USD conversion and formatting.
 *
 * `convertCopToUsd` mirrors `services/exchange_rate.convert_cop_to_usd` exactly,
 * including its `not cop_per_usd` guard: a zero rate is unusable, not a division
 * by zero, and returning `null` is what lets the UI say "no rate" instead of
 * rendering `Infinity`.
 */
export function convertCopToUsd(
  amountCop: number | null | undefined,
  copPerUsd: number | null | undefined,
): number | null {
  if (amountCop == null || !Number.isFinite(amountCop)) {
    return null;
  }

  if (copPerUsd == null || !Number.isFinite(copPerUsd) || copPerUsd === 0) {
    return null;
  }

  return amountCop / copPerUsd;
}

const copFormatter = new Intl.NumberFormat('es-CO', {
  currency: 'COP',
  maximumFractionDigits: 0,
  style: 'currency',
});

const usdFormatter = new Intl.NumberFormat('en-US', {
  currency: 'USD',
  maximumFractionDigits: 0,
  style: 'currency',
});

/** The placeholder for a figure that exists but cannot be shown honestly. */
export const UNAVAILABLE = '—';

export function formatCop(amountCop: number | null | undefined): string {
  if (amountCop == null || !Number.isFinite(amountCop)) {
    return UNAVAILABLE;
  }

  return copFormatter.format(amountCop);
}

export function formatUsd(amountUsd: number | null | undefined): string {
  if (amountUsd == null || !Number.isFinite(amountUsd)) {
    return UNAVAILABLE;
  }

  return usdFormatter.format(amountUsd);
}

/**
 * The rate a conversion was made with, stated alongside where it came from.
 *
 * `'report'` is a rate frozen at the moment an analysis ran; `'live'` is
 * today's. They will disagree, and the UI's job is to say which one produced
 * the number on screen rather than to reconcile them.
 */
export type RateSource = 'live' | 'report';

export type CurrencyRate = {
  rate: number;
  /** ISO date string the rate is for. */
  rateAsOf: string;
  rateSource: RateSource;
};

const dateFormatter = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'short',
  timeZone: 'UTC',
  year: 'numeric',
});

/**
 * "COP 4,013 / USD · 12 Aug 2026 (as analysed)".
 *
 * Rendered wherever a converted figure is, because a USD number whose rate is
 * not stated is the exact ambiguity `useCurrency`'s required rate argument
 * exists to prevent.
 */
export function formatRateProvenance({
  rate,
  rateAsOf,
  rateSource,
}: CurrencyRate): string {
  const qualifier = rateSource === 'report' ? ' (as analysed)' : '';
  const formattedRate = new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0,
  }).format(rate);

  return `COP ${formattedRate} / USD · ${formatRateDate(rateAsOf)}${qualifier}`;
}

function formatRateDate(rateAsOf: string): string {
  const parsed = new Date(rateAsOf);

  if (Number.isNaN(parsed.getTime())) {
    return rateAsOf;
  }

  return dateFormatter.format(parsed);
}
