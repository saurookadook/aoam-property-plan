import { describe, expect, it, vi } from 'vitest';

import { formatReportAmount, reportCurrencyRate } from '../utils';

describe('reportCurrencyRate', () => {
  it('is null when the report has no exchange rate', () => {
    expect(
      reportCurrencyRate({ exchange_rate: null, calculated_at: '2026-08-20T00:00:00Z' }),
    ).toBeNull();
  });

  it('carries the report rate, tagged as "report"', () => {
    expect(
      reportCurrencyRate({
        exchange_rate: 4013,
        calculated_at: '2026-08-20T02:06:09.952335Z',
      }),
    ).toEqual({
      rate: 4013,
      rateAsOf: '2026-08-20T02:06:09.952335Z',
      rateSource: 'report',
    });
  });
});

describe('formatReportAmount', () => {
  it('falls back to a plain COP string when there is no rate', () => {
    expect(formatReportAmount({} as never, null, 620000000)).toEqual({
      text: expect.stringContaining('620'),
      provenance: null,
      isUnavailable: false,
    });
  });

  it('uses formatStoredPair when a usd sibling is supplied', () => {
    const formatStoredPair = vi.fn().mockReturnValue({
      text: '$154,498',
      provenance: 'report',
      isUnavailable: false,
    });
    const currency = { formatFromCop: vi.fn(), formatStoredPair };
    const rate = { rate: 4013, rateAsOf: '2026-08-20', rateSource: 'report' } as const;

    formatReportAmount(currency, rate, 620000000, 154497.88);

    expect(formatStoredPair).toHaveBeenCalledWith(620000000, 154497.88, rate);
    expect(currency.formatFromCop).not.toHaveBeenCalled();
  });

  it('uses formatFromCop when no usd sibling exists on the column', () => {
    const formatFromCop = vi.fn().mockReturnValue({
      text: '$1,000',
      provenance: 'report',
      isUnavailable: false,
    });
    const currency = { formatFromCop, formatStoredPair: vi.fn() };
    const rate = { rate: 4013, rateAsOf: '2026-08-20', rateSource: 'report' } as const;

    formatReportAmount(currency, rate, 4013000);

    expect(formatFromCop).toHaveBeenCalledWith(4013000, rate);
    expect(currency.formatStoredPair).not.toHaveBeenCalled();
  });
});
