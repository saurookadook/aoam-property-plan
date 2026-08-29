import { useEffect, useMemo, useState } from 'react';

import type { MarketWithFinancialReportEntity, PropertyEntity } from '@/types';
import { BUDGET_COP } from '@/constants';
import type { CurrencyRate } from '@/common/utils/currency';
import { FlexColumn, FlexRow } from '@/layouts';
import { ColombiaMap } from '../ColombiaMap';
import { MarketCard, marketCardElementId } from '../MarketCard';
import { MarketSortControls } from '../MarketSortControls';
import { sortMarkets, type MarketSortKey } from '../../utils/sortMarkets';

import './styles.scss';

function groupPurchasePricesByMarketId(
  properties: readonly PropertyEntity[],
): Map<string, number[]> {
  const pricesByMarketId = new Map<string, number[]>();

  for (const property of properties) {
    if (property.market_id == null || property.purchase_price_cop == null) {
      continue;
    }

    const prices = pricesByMarketId.get(property.market_id) ?? [];
    prices.push(property.purchase_price_cop);
    pricesByMarketId.set(property.market_id, prices);
  }

  return pricesByMarketId;
}

export function MarketsListData({
  marketsListData,
  propertiesListData,
  rate,
}: {
  marketsListData: MarketWithFinancialReportEntity[];
  propertiesListData: PropertyEntity[];
  rate: CurrencyRate | null;
}) {
  const [sortKey, setSortKey] = useState<MarketSortKey>('fit');
  const [selectedMarketId, setSelectedMarketId] = useState<string | null>(null);

  const sortedMarkets = useMemo(
    () => sortMarkets(marketsListData, sortKey),
    [marketsListData, sortKey],
  );

  const pricesByMarketId = useMemo(
    () => groupPurchasePricesByMarketId(propertiesListData),
    [propertiesListData],
  );

  useEffect(() => {
    if (selectedMarketId == null) {
      return;
    }

    document
      .getElementById(marketCardElementId(selectedMarketId))
      ?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, [selectedMarketId]);

  return (
    <FlexColumn id="markets-list-data" className="markets-list-data">
      <MarketSortControls sortKey={sortKey} onSortKeyChange={setSortKey} />

      <ColombiaMap markets={marketsListData} onSelectMarket={setSelectedMarketId} />

      <FlexRow className="markets-list-data__grid">
        {sortedMarkets.map((market) => (
          <MarketCard
            key={market.id}
            budgetCop={BUDGET_COP}
            isSelected={market.id === selectedMarketId}
            market={market}
            purchasePricesCop={pricesByMarketId.get(market.id) ?? []}
            rate={rate}
          />
        ))}
      </FlexRow>
    </FlexColumn>
  );
}
