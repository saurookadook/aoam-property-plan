import { describe, expect, it } from 'vitest';

import { dataConfidence } from '../dataConfidence';

describe('dataConfidence', () => {
  it('rates a well-corroborated comp-derived figure as good', () => {
    expect(dataConfidence('comp_derived', 12)).toEqual({
      level: 'good',
      message: 'Good confidence — median of 12 comparable listings.',
    });
  });

  it('rates a 5-9 comp figure as fair', () => {
    expect(dataConfidence('comp_derived', 6).level).toBe('fair');
    expect(dataConfidence('comp_derived', 5).level).toBe('fair');
  });

  it('rates a thinly corroborated comp-derived figure as low', () => {
    expect(dataConfidence('comp_derived', 4).level).toBe('low');
    expect(dataConfidence('comp_derived', 2).message).toContain(
      '2 comparable listings',
    );
  });

  it("names the count in Calima's single-comp case", () => {
    // The report that motivated all of this: AirROI's p25 estimate, checked
    // against exactly one comp - a 5br/16-guest property returned for a 2br
    // query. The singular matters, because "1 comparable listings" reads as a
    // rounding artefact rather than the warning it is.
    expect(dataConfidence('airroi_p25_thin_comps', 1)).toEqual({
      level: 'low',
      message: "Low confidence — AirROI's model only, 1 comparable listing.",
    });
  });

  it.each(['airroi_p25', 'airroi_avg', 'airroi_avg_thin_comps'] as const)(
    'treats %s as low confidence however many comps came back',
    (source) => {
      // A model estimate is a model estimate. Comps that were not used to derive
      // the figure do not corroborate it.
      expect(dataConfidence(source, 40).level).toBe('low');
    },
  );

  it('reports an unanalysed property as unknown, not as bad', () => {
    expect(dataConfidence(null, null)).toEqual({
      level: 'unknown',
      message: 'This property has not been analysed yet.',
    });
  });
});
