import { describe, expect, it } from 'vitest';

import { cocReturnTone, paybackTone } from '../metricThresholds';

describe('cocReturnTone', () => {
  it.each([
    [12, 'good'],
    [8, 'good'],
    [5, 'fair'],
    [4, 'fair'],
    [1.5, 'poor'],
    [-14, 'poor'],
  ] as const)('tones %d%% as %s at good confidence', (value, expected) => {
    expect(cocReturnTone(value, 'good')).toBe(expected);
  });

  it('withholds the judgement entirely when confidence is low', () => {
    // The most dangerous pixel in this app: a green CoC return computed off
    // AirROI's model with a single comparable behind it. The number is still
    // shown; the recommendation is not.
    expect(cocReturnTone(14.2, 'low')).toBe('unrated');
  });

  it('is unrated for an unanalysed property', () => {
    expect(cocReturnTone(null, 'unknown')).toBe('unrated');
  });

  it('is unrated for a missing figure even at good confidence', () => {
    expect(cocReturnTone(null, 'good')).toBe('unrated');
  });
});

describe('paybackTone', () => {
  it('inverts the comparison - fewer years is better', () => {
    expect(paybackTone(9, 'good')).toBe('good');
    expect(paybackTone(16, 'good')).toBe('fair');
    expect(paybackTone(31, 'good')).toBe('poor');
  });

  it('is unrated when confidence is low', () => {
    expect(paybackTone(9, 'low')).toBe('unrated');
  });

  it('is unrated for a property that never pays back', () => {
    expect(paybackTone(null, 'good')).toBe('unrated');
  });
});
