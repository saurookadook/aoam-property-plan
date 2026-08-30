import classNames from 'classnames';
import { Link as RouterLink } from 'react-router';
import { Card, CardContent, Chip, Typography } from '@mui/material';

import type { MarketWithFinancialReportEntity } from '@/types';
import { investmentFit } from '@/common/utils/investmentFit';
import { formatCop, type CurrencyRate } from '@/common/utils/currency';
import { useCurrency } from '@/providers';
import { FlexColumn, FlexRow } from '@/layouts';
import { BudgetIndicator } from './BudgetIndicator';
import { FitScoreBadge } from '../FitScoreBadge';

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

  const formatMoney = (amountCop: number) =>
    rate != null ? formatFromCop(amountCop, rate).text : formatCop(amountCop);

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
          <FlexColumn className="market-card__metrics">
            <Typography component="span">ADR: {formatMoney(report.adr_cop)}</Typography>
            <Typography component="span">
              Occupancy: {(report.occupancy_rate * 100).toFixed(0)}%
            </Typography>
            <Typography component="span">
              Annual revenue: {formatMoney(report.annual_revenue_cop)}
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

            <BudgetIndicator
              budgetCop={budgetCop}
              purchasePricesCop={purchasePricesCop}
            />
          </FlexColumn>
        )}
      </CardContent>
    </Card>
  );
}
