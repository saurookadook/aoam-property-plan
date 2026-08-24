import { describe, expect, it } from 'vitest';

import {
  UNAVAILABLE,
  convertCopToUsd,
  formatCop,
  formatRateProvenance,
  formatUsd,
} from '../currency';

describe('convertCopToUsd', () => {
  it('divides the COP amount by the rate', () => {
    expect(convertCopToUsd(4_013_000, 4013)).toBe(1000);
  });

  it.each([
    ['a null amount', null, 4013],
    ['an undefined amount', undefined, 4013],
    ['a null rate', 4_013_000, null],
    // Mirrors the backend's `not cop_per_usd` guard: a zero rate is unusable,
    // and returning `Infinity` would render as a plausible-looking figure.
    ['a zero rate', 4_013_000, 0],
    ['a non-finite amount', Number.NaN, 4013],
  ])('returns null for %s', (_label, amount, rate) => {
    expect(convertCopToUsd(amount, rate)).toBeNull();
  });
});

describe('formatCop / formatUsd', () => {
  it('formats COP grouped and with no decimal places', () => {
    // Locale-dependent separators and a non-breaking space after the symbol, so
    // assert on the digits rather than the exact string.
    expect(formatCop(850_000_000).replace(/\D/g, '')).toBe('850000000');
  });

  it('formats USD', () => {
    expect(formatUsd(211_812)).toBe('$211,812');
  });

  it('renders the placeholder rather than NaN for an absent figure', () => {
    expect(formatCop(null)).toBe(UNAVAILABLE);
    expect(formatUsd(undefined)).toBe(UNAVAILABLE);
  });
});

describe('formatRateProvenance', () => {
  it('marks a report rate as the one the analysis was run at', () => {
    expect(
      formatRateProvenance({
        rate: 4013,
        rateAsOf: '2026-08-12',
        rateSource: 'report',
      }),
    ).toBe('COP 4,013 / USD · 12 Aug 2026 (as analysed)');
  });

  it('leaves a live rate unqualified', () => {
    expect(
      formatRateProvenance({
        rate: 4087,
        rateAsOf: '2026-08-20',
        rateSource: 'live',
      }),
    ).toBe('COP 4,087 / USD · 20 Aug 2026');
  });
});
