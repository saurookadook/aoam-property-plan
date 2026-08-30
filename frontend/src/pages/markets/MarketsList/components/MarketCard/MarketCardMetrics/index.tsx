import { Chip, Typography } from '@mui/material';

import type { MarketFinancialReportEntity } from '@/types';
import { FlexColumn, FlexRow } from '@/layouts';
import { BudgetIndicator } from '../BudgetIndicator';

export function MarketCardMetrics({
  budgetCop,
  formatMoneyFn,
  purchasePricesCop,
  report,
}: {
  budgetCop: number;
  formatMoneyFn: (amountCop: number) => string;
  purchasePricesCop: readonly (number | null | undefined)[];
  report: MarketFinancialReportEntity;
}) {
  return (
    <FlexColumn className="market-card__metrics">
      <Typography component="span">ADR: {formatMoneyFn(report.adr_cop)}</Typography>
      <Typography component="span">
        Occupancy: {(report.occupancy_rate * 100).toFixed(0)}%
      </Typography>
      <Typography component="span">
        Annual revenue: {formatMoneyFn(report.annual_revenue_cop)}
      </Typography>
      <Typography component="span">
        {Math.round(report.listing_count)} avg. active listings (12 mo)
      </Typography>

      <FlexRow className="market-card__peak-months">
        {report.peak_months == null ? (
          <Typography component="span" variant="body2">
            Peak months not yet available
          </Typography>
        ) : (
          report.peak_months.map((month) => (
            <Chip key={month} label={month} size="small" />
          ))
        )}
      </FlexRow>

      <BudgetIndicator budgetCop={budgetCop} purchasePricesCop={purchasePricesCop} />
    </FlexColumn>
  );
}
