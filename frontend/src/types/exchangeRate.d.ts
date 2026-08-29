/**
 * Mirrors `api/models/exchange_rate.ExchangeRateData`.
 *
 * Deliberately narrow: the rate and the day it was true, nothing else. A figure
 * shown without saying when it was true is worse than no figure.
 */
export type ExchangeRateData = {
  cop_per_usd: number;
  /** ISO date string (`YYYY-MM-DD`) - a `date`, not a `datetime`, on the backend. */
  record_date: string;
};
