import { Typography } from '@mui/material';

import { filterPricedValues, medianPurchasePriceCop } from '@/common/utils/investmentFit';
import { formatCop } from '@/common/utils/currency';

import './styles.scss';

/**
 * How many properties at the median asking price a fixed budget would cover,
 * or an honest "not enough data" below three priced rows in this market.
 *
 * The median is a real number from scraped `properties`, never a report
 * figure - `BUDGET_COP` and a market's ADR/revenue answer different questions.
 */
export function BudgetIndicator({
  budgetCop,
  purchasePricesCop,
}: {
  budgetCop: number;
  purchasePricesCop: readonly (number | null | undefined)[];
}) {
  const pricedCount = filterPricedValues(purchasePricesCop).length;
  const medianCop = medianPurchasePriceCop(purchasePricesCop);

  if (medianCop == null) {
    return (
      <Typography className="budget-indicator budget-indicator--insufficient" variant="body2">
        {`Not enough price data (${pricedCount})`}
      </Typography>
    );
  }

  const propertiesAffordable = Math.floor(budgetCop / medianCop);

  return (
    <Typography className="budget-indicator" variant="body2">
      {`Budget covers ~${propertiesAffordable} at median price (${formatCop(medianCop)})`}
    </Typography>
  );
}
