import { Typography } from '@mui/material';

import { barGeometry, referenceLineY } from '@/common/utils/charts';
import { FlexColumn } from '@/layouts';

import './styles.scss';

const MONTH_NAMES = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

const WIDTH = 360;
const HEIGHT = 140;
const ANNUAL_MEAN = 1 / 12;
const PEAK_THRESHOLD = ANNUAL_MEAN * 1.15;

/**
 * Twelve `<rect>`s over a `viewBox`, not a charting dependency - the entire
 * requirement for twelve floats summing to 1.0 is `y = value / max * height`.
 * Two reference lines turn the bars into an argument: the solid line is the
 * annual mean (1/12), the dashed line is the doc's own +15% peak threshold,
 * which `peak_months` deliberately does not use (see `handle_markets_peak_months`
 * - it takes the top three months instead, because Step 6 measured a real
 * property clearing +15% in zero months).
 */
export function SeasonalityChart({
  distribution,
}: {
  distribution: number[] | null | undefined;
}) {
  if (distribution == null || distribution.length !== 12) {
    return (
      <Typography className="seasonality-chart__empty" variant="body2">
        Seasonality not yet available.
      </Typography>
    );
  }

  const bars = barGeometry(distribution, { width: WIDTH, height: HEIGHT });
  const meanY = referenceLineY(distribution, ANNUAL_MEAN, HEIGHT);
  const peakY = referenceLineY(distribution, PEAK_THRESHOLD, HEIGHT);

  return (
    <FlexColumn className="seasonality-chart">
      <Typography variant="h3">Monthly revenue seasonality</Typography>

      <svg
        className="seasonality-chart__svg"
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        role="img"
        aria-label="Monthly share of annual revenue"
      >
        <line
          className="seasonality-chart__mean-line"
          x1={0}
          x2={WIDTH}
          y1={meanY}
          y2={meanY}
        />
        <line
          className="seasonality-chart__peak-line"
          x1={0}
          x2={WIDTH}
          y1={peakY}
          y2={peakY}
        />

        {bars.map((bar, index) => (
          <rect
            key={MONTH_NAMES[index]}
            className="seasonality-chart__bar"
            x={bar.x}
            y={bar.y}
            width={bar.w}
            height={bar.h}
          >
            <title>{`${MONTH_NAMES[index]} — ${(distribution[index] * 100).toFixed(1)}% of annual revenue`}</title>
          </rect>
        ))}
      </svg>
    </FlexColumn>
  );
}
