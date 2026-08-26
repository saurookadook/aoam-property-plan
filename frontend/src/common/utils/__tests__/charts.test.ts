import { describe, expect, it } from 'vitest';

import { barGeometry, referenceLineY } from '../charts';

/** Twelve fractions summing to 1.0, as `monthly_revenue_distribution` is. */
const DISTRIBUTION = [
  0.1042, 0.0788, 0.0796, 0.0731, 0.0724, 0.0869, 0.1058, 0.0913, 0.0702, 0.0714,
  0.0716, 0.0947,
];

describe('barGeometry', () => {
  it('produces one rect per value', () => {
    expect(barGeometry(DISTRIBUTION, { width: 480, height: 200 })).toHaveLength(12);
  });

  it('scales the tallest bar to the full height', () => {
    const bars = barGeometry(DISTRIBUTION, { width: 480, height: 200 });
    const july = bars[6];

    expect(july.h).toBeCloseTo(200, 10);
    expect(july.y).toBeCloseTo(0, 10);
  });

  it('scales against the maximum, not the sum', () => {
    // Scaling twelve near-equal fractions against their sum would flatten every
    // bar into a sliver and hide the very peaks the chart is asked about.
    const bars = barGeometry([0.5, 0.25], { width: 100, height: 100, gap: 0 });

    expect(bars[0].h).toBe(100);
    expect(bars[1].h).toBe(50);
  });

  it('lays bars out left to right with a symmetric gap', () => {
    const bars = barGeometry([1, 1], { width: 100, height: 10, gap: 0.2 });

    expect(bars[0]).toEqual({ x: 5, y: 0, w: 40, h: 10 });
    expect(bars[1]).toEqual({ x: 55, y: 0, w: 40, h: 10 });
  });

  it('yields zero-height bars rather than NaN when every value is zero', () => {
    // An all-zero distribution is a real state. `NaN` in an SVG attribute
    // renders as nothing, with no indication of why.
    const bars = barGeometry([0, 0, 0], { width: 90, height: 50 });

    expect(bars.every((bar) => bar.h === 0 && bar.y === 50)).toBe(true);
  });

  it('returns nothing for an empty series', () => {
    expect(barGeometry([], { width: 100, height: 100 })).toEqual([]);
  });
});

describe('referenceLineY', () => {
  it('places the annual mean on the same scale as the bars', () => {
    const height = 200;
    const mean = 1 / 12;
    const bars = barGeometry(DISTRIBUTION, { width: 480, height });
    const meanY = referenceLineY(DISTRIBUTION, mean, height);

    // September is below the mean, July above it - so the line falls between.
    expect(meanY).toBeGreaterThan(bars[6].y);
    expect(meanY).toBeLessThan(bars[8].y);
  });

  it('clamps a reference above the maximum to the top edge', () => {
    expect(referenceLineY(DISTRIBUTION, 1, 200)).toBe(0);
  });

  it('sits on the baseline when there is nothing to scale against', () => {
    expect(referenceLineY([0, 0], 0.5, 200)).toBe(200);
  });
});
