import { useEffect, useMemo, useState } from 'react';

import type { MarketWithFinancialReportEntity, PropertyEntity } from '@/types';
import { BUDGET_COP } from '@/constants';
import type { CurrencyRate } from '@/common/utils/currency';
import { FlexColumn, FlexRow } from '@/layouts';
import {
  sortMarkets,
  type MarketSortKey,
} from '@/pages/markets/MarketsList/utils/sortMarkets';
import { groupPurchasePricesByMarketId } from '@/pages/markets/MarketsList/utils/dataProcessing';
import { ColombiaMap } from '../ColombiaMap';
import { MarketCard, marketCardElementId } from '../MarketCard';
import { MarketSortControls } from '../MarketSortControls';

import './styles.scss';

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
    <FlexRow id="markets-list-data" className="markets-list-data">
      <FlexColumn style={{ maxWidth: '50%' }}>
        <MarketSortControls onSortKeyChange={setSortKey} sortKey={sortKey} />

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

      <ColombiaMap markets={marketsListData} onSelectMarket={setSelectedMarketId} />
    </FlexRow>
  );
}
