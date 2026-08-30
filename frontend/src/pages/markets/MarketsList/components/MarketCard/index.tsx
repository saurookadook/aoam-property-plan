import { useCallback } from 'react';
import classNames from 'classnames';
import { Link as RouterLink } from 'react-router';
import { Card, CardContent, Typography } from '@mui/material';

import type { MarketWithFinancialReportEntity } from '@/types';
import { investmentFit } from '@/common/utils/investmentFit';
import { formatCop, type CurrencyRate } from '@/common/utils/currency';
import { useCurrency } from '@/providers';
import { FlexRow } from '@/layouts';
import { FitScoreBadge } from '../FitScoreBadge';
import { MarketCardMetrics } from './MarketCardMetrics';

import './styles.scss';

/** DOM id `ColombiaMap` scrolls to when a marker is clicked. */
export function marketCardElementId(marketId: string): string {
  return `market-card-${marketId}`;
}

export function MarketCard({
  budgetCop,
  isSelected = false,
  market,
  purchasePricesCop,
  rate,
}: {
  budgetCop: number;
  isSelected?: boolean;
  market: MarketWithFinancialReportEntity;
  purchasePricesCop: readonly (number | null | undefined)[];
  rate: CurrencyRate | null;
}) {
  const { formatFromCop } = useCurrency();
  const report = market.financial_report;
  const fit = investmentFit(market);

  const formatMoney = useCallback(
    (amountCop: number) => {
      if (rate != null) {
        return formatFromCop(amountCop, rate).text;
      }

      return formatCop(amountCop);
    },
    [formatFromCop, rate],
  );

  return (
    <Card
      id={marketCardElementId(market.id)}
      className={classNames('market-card', { 'market-card--selected': isSelected })}
    >
      <CardContent>
        <FlexRow className="market-card__header">
          <Typography variant="h3" className="market-card__header-text">
            <RouterLink to={`/markets/${market.id}`}>{market.locality}</RouterLink>
          </Typography>
        </FlexRow>

        <hr />

        <FitScoreBadge fit={fit} />

        <hr />

        {market.locality === 'Cali' && (
          <Typography className="market-card__note" variant="caption">
            AirROI has no separate Granada or El Peñón market - both resolve to Cali.
          </Typography>
        )}

        {report == null ? (
          <Typography className="market-card__empty-state" variant="body2">
            No financial report yet - this market has not been summarised.
          </Typography>
        ) : (
          <MarketCardMetrics
            budgetCop={budgetCop}
            formatMoneyFn={formatMoney}
            purchasePricesCop={purchasePricesCop}
            report={report}
          />
        )}
      </CardContent>
    </Card>
  );
}
