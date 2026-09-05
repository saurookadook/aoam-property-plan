import { useQuery } from '@tanstack/react-query';

import type { ExchangeRateData } from '@/types';
import { API_SERVER_DOMAIN } from '@/constants';
import { fetchy, unwrapEnvelope } from '@/utils';

/** Shared with every query on Step 10's hour-long stale time. */
export const HOUR_STALE_TIME = 1000 * 60 * 60;

/**
 * A `useQuery`, not a suspense query - deliberately. A market card's ADR /
 * occupancy / revenue always have their `_usd` siblings NULL, and a property
 * with no report yet has no stored `exchange_rate` either, so this live rate is
 * the only way either page's currency toggle can work at all. Its own failure
 * (a 503, or a cold cache) should degrade the page to COP rather than take the
 * whole page down, which is why it is not in either page's loader.
 */
export function useExchangeRateQuery() {
  return useQuery({
    queryKey: ['exchangeRate'],
    queryFn: async () => {
      const exchangeRate = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/exchange-rate`) // force formatting
        .then(unwrapEnvelope<ExchangeRateData>);

      return { exchangeRate };
    },
    staleTime: HOUR_STALE_TIME,
    retry: false,
  });
}
