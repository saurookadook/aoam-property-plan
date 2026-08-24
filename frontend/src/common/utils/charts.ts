export type BarRect = {
  x: number;
  y: number;
  w: number;
  h: number;
};

export type BarGeometryOptions = {
  width: number;
  height: number;
  /** Fraction of each slot left empty, split either side of the bar. */
  gap?: number;
};

export const DEFAULT_BAR_GAP = 0.2;

/**
 * Bar rectangles for a plain-SVG chart, in user units over a `viewBox`.
 *
 * The whole charting requirement for twelve floats summing to 1.0 is
 * `y = value / max * height`, which is why this is arithmetic in a pure function
 * rather than a charting dependency. Keeping the geometry separate from the JSX
 * is also what makes it unit-testable without rendering anything.
 *
 * Bars are scaled against the **maximum**, not the sum: the chart's question is
 * "which months are the peaks", and scaling against the sum would flatten twelve
 * near-equal fractions into twelve near-invisible slivers.
 *
 * A non-positive maximum yields zero-height bars rather than `NaN`s - a report
 * whose distribution is all zeroes is a real state, and an SVG full of `NaN`
 * attributes renders as nothing with no indication why.
 */
export function barGeometry(
  values: readonly number[],
  { width, height, gap = DEFAULT_BAR_GAP }: BarGeometryOptions,
): BarRect[] {
  if (values.length === 0) {
    return [];
  }

  const slot = width / values.length;
  const clampedGap = Math.min(Math.max(gap, 0), 1);
  const barWidth = slot * (1 - clampedGap);
  const offset = (slot - barWidth) / 2;

  const max = values.reduce(
    (highest, value) => (Number.isFinite(value) && value > highest ? value : highest),
    0,
  );

  return values.map((value, index) => {
    const safeValue = Number.isFinite(value) && value > 0 ? value : 0;
    const barHeight = max > 0 ? (safeValue / max) * height : 0;

    return {
      x: index * slot + offset,
      y: height - barHeight,
      w: barWidth,
      h: barHeight,
    };
  });
}

/**
 * The `y` a horizontal reference line sits at, on the same scale as the bars.
 *
 * The seasonality chart draws two: the annual mean (1/12) and the +15%
 * threshold. Sharing `max` with `barGeometry` is what keeps them on the same
 * scale as the bars they are meant to be read against.
 */
export function referenceLineY(
  values: readonly number[],
  value: number,
  height: number,
): number {
  const max = values.reduce(
    (highest, candidate) =>
      Number.isFinite(candidate) && candidate > highest ? candidate : highest,
    0,
  );

  if (max <= 0) {
    return height;
  }

  return height - Math.min(value / max, 1) * height;
}
