import { Tooltip, Typography } from '@mui/material';

import type { SensitivityCell } from '@/types';
import { useCurrency } from '@/providers';
import type { CurrencyRate } from '@/common/utils/currency';
import { FlexColumn } from '@/layouts';
import { formatReportAmount } from '../../utils';

import './styles.scss';

const COLUMN_LABEL: Record<number, string> = {
  0.9: '-10%',
  1.0: 'Base',
  1.1: '+10%',
};

/**
 * The doc's 3x3 sensitivity grid is arithmetic theatre: revenue is
 * `ADR * occupancy * 365`, so both axes scale the same product and the nine
 * cells collapse to six values with a repeating anti-diagonal. This is the
 * backend's real 3-cell revenue sweep instead.
 */
export function SensitivityTable({
  cells,
  rate,
}: {
  cells: SensitivityCell[];
  rate: CurrencyRate | null;
}) {
  const currency = useCurrency();

  if (cells.length === 0) {
    return null;
  }

  const sorted = [...cells].sort((a, b) => a.revenue_factor - b.revenue_factor);

  return (
    <FlexColumn className="sensitivity-table">
      <Tooltip title="Both axes of a 3x3 grid would scale the same product (ADR x occupancy x 365), collapsing to a repeating anti-diagonal - so this varies revenue alone.">
        <Typography variant="h3">Revenue sensitivity</Typography>
      </Tooltip>

      <table>
        <thead>
          <tr>
            <th scope="col" />
            {sorted.map((cell) => (
              <th key={cell.revenue_factor} scope="col">
                {COLUMN_LABEL[cell.revenue_factor] ?? `${Math.round(cell.revenue_factor * 100)}%`}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          <tr>
            <th scope="row">Annual revenue</th>
            {sorted.map((cell) => (
              <td key={cell.revenue_factor}>
                {formatReportAmount(currency, rate, cell.annual_revenue_cop).text}
              </td>
            ))}
          </tr>

          <tr>
            <th scope="row">Cash-on-cash return</th>
            {sorted.map((cell) => (
              <td key={cell.revenue_factor}>{cell.coc_return_percentage.toFixed(1)}%</td>
            ))}
          </tr>

          <tr>
            <th scope="row">Payback period</th>
            {sorted.map((cell) => (
              <td key={cell.revenue_factor}>
                {cell.payback_years == null ? '—' : `${cell.payback_years.toFixed(1)} yr`}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </FlexColumn>
  );
}
