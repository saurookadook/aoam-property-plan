import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type PropsWithChildren,
} from 'react';

import {
  convertCopToUsd,
  formatCop,
  formatRateProvenance,
  formatUsd,
  type CurrencyRate,
} from '@/common/utils/currency';

export type CurrencyCode = 'COP' | 'USD';

export const currencyStorageKey = 'aoam-display-currency';

type CurrencyContextValue = {
  currency: CurrencyCode;
  setCurrency: (currency: CurrencyCode) => void;
  toggleCurrency: () => void;
};

const CurrencyContext = createContext<CurrencyContextValue | null>(null);

function readStoredCurrency(): CurrencyCode {
  try {
    return window.localStorage.getItem(currencyStorageKey) === 'USD' ? 'USD' : 'COP';
  } catch {
    // Storage is unavailable in some embedded contexts; COP is the source of
    // truth for every figure the API serves, so it is the safe default.
    return 'COP';
  }
}

export function CurrencyProvider({ children }: PropsWithChildren) {
  const [currency, setCurrencyState] = useState<CurrencyCode>(readStoredCurrency);

  const setCurrency = useCallback((next: CurrencyCode) => {
    setCurrencyState(next);
    try {
      window.localStorage.setItem(currencyStorageKey, next);
    } catch {
      // A preference that cannot be persisted is still a valid preference.
    }
  }, []);

  const toggleCurrency = useCallback(() => {
    setCurrency(currency === 'COP' ? 'USD' : 'COP');
  }, [currency, setCurrency]);

  const value = useMemo(
    () => ({ currency, setCurrency, toggleCurrency }),
    [currency, setCurrency, toggleCurrency],
  );

  return <CurrencyContext value={value}>{children}</CurrencyContext>;
}

export type FormattedAmount = {
  /** The figure, already in the selected currency. */
  text: string;
  /** `null` when the selected currency is COP, or when no conversion was made. */
  provenance: string | null;
  /** `true` when USD was asked for and the rate could not produce it. */
  isUnavailable: boolean;
};

export type UseCurrencyValue = CurrencyContextValue & {
  /**
   * Formats a COP amount in the selected currency.
   *
   * The rate is a **required argument**, not something the hook holds. That is
   * the whole design: a property report's `_usd` columns were computed with
   * `report.exchange_rate`, market cards have no rate they were computed at and
   * must use today's, and a hook carrying one ambient rate would silently mix
   * the two. Making the caller name `{rate, rateAsOf, rateSource}` at the point
   * of conversion makes that mistake impossible to make quietly.
   */
  formatFromCop: (
    amountCop: number | null | undefined,
    rate: CurrencyRate,
  ) => FormattedAmount;
  /**
   * Picks between a stored COP column and its stored USD sibling, doing no
   * arithmetic at all.
   *
   * For a property report this is the correct path: every `_usd` column was
   * computed with the same `report.exchange_rate`, so re-deriving from it would
   * risk showing a net income that does not equal
   * `annual_revenue_usd - 12 * monthly_expenses_usd` from the same row.
   */
  formatStoredPair: (
    amountCop: number | null | undefined,
    amountUsd: number | null | undefined,
    rate: CurrencyRate,
  ) => FormattedAmount;
};

export function useCurrency(): UseCurrencyValue {
  const context = useContext(CurrencyContext);

  if (context == null) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }

  const { currency } = context;

  const formatFromCop = useCallback(
    (amountCop: number | null | undefined, rate: CurrencyRate): FormattedAmount => {
      if (currency === 'COP') {
        return { text: formatCop(amountCop), provenance: null, isUnavailable: false };
      }

      const amountUsd = convertCopToUsd(amountCop, rate?.rate);

      return {
        text: formatUsd(amountUsd),
        provenance: rate == null ? null : formatRateProvenance(rate),
        isUnavailable: amountUsd == null && amountCop != null,
      };
    },
    [currency],
  );

  const formatStoredPair = useCallback(
    (
      amountCop: number | null | undefined,
      amountUsd: number | null | undefined,
      rate: CurrencyRate,
    ): FormattedAmount => {
      if (currency === 'COP') {
        return { text: formatCop(amountCop), provenance: null, isUnavailable: false };
      }

      return {
        text: formatUsd(amountUsd),
        provenance: rate == null ? null : formatRateProvenance(rate),
        isUnavailable: amountUsd == null && amountCop != null,
      };
    },
    [currency],
  );

  return { ...context, formatFromCop, formatStoredPair };
}
