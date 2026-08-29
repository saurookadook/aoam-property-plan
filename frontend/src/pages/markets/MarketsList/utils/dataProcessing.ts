import type { PropertyEntity } from '@/types';

export function groupPurchasePricesByMarketId(
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
