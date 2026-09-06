import { Card, CardContent, Typography } from '@mui/material';

import type { MonthlyExpenseBreakdown } from '@/types';
import { useCurrency } from '@/providers';
import type { CurrencyRate } from '@/common/utils/currency';
import { FlexColumn, FlexRow } from '@/layouts';
import { formatReportAmount } from '../../utils';

import './styles.scss';

const LINES: { key: keyof MonthlyExpenseBreakdown; label: string }[] = [
  { key: 'mortgage_cop', label: 'Mortgage' },
  { key: 'hoa_cop', label: 'HOA' },
  { key: 'management_fee_cop', label: 'Management fee' },
  { key: 'maintenance_reserve_cop', label: 'Maintenance reserve' },
  { key: 'predial_cop', label: 'Predial (property tax)' },
];

export function ExpenseBreakdownCard({
  expenses,
  rate,
}: {
  expenses: MonthlyExpenseBreakdown;
  rate: CurrencyRate | null;
}) {
  const currency = useCurrency();

  return (
    <Card className="expense-breakdown-card">
      <CardContent>
        <Typography variant="h3">Monthly expenses</Typography>

        <FlexColumn className="expense-breakdown-card__lines">
          {LINES.map(({ key, label }) => (
            <FlexRow key={key} className="expense-breakdown-card__line">
              <Typography component="span">{label}</Typography>
              <Typography component="span">
                {formatReportAmount(currency, rate, expenses[key]).text}
              </Typography>
            </FlexRow>
          ))}

          <FlexRow className="expense-breakdown-card__line expense-breakdown-card__line--total">
            <Typography component="span">Total</Typography>
            <Typography component="span">
              {formatReportAmount(currency, rate, expenses.total_cop).text}
            </Typography>
          </FlexRow>
        </FlexColumn>
      </CardContent>
    </Card>
  );
}
