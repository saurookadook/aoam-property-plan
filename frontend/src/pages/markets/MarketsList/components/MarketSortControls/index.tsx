import { ToggleButton, ToggleButtonGroup } from '@mui/material';

import { MARKET_SORT_OPTIONS, type MarketSortKey } from '../../utils/sortMarkets';

import './styles.scss';

export function MarketSortControls({
  sortKey,
  onSortKeyChange,
}: {
  sortKey: MarketSortKey;
  onSortKeyChange: (sortKey: MarketSortKey) => void;
}) {
  return (
    <ToggleButtonGroup
      aria-label="Sort markets by"
      className="market-sort-controls"
      color="primary"
      exclusive
      size="small"
      value={sortKey}
      onChange={(_event, nextSortKey: MarketSortKey | null) => {
        if (nextSortKey != null) {
          onSortKeyChange(nextSortKey);
        }
      }}
    >
      {MARKET_SORT_OPTIONS.map((option) => (
        <ToggleButton key={option.key} value={option.key}>
          {option.label}
        </ToggleButton>
      ))}
    </ToggleButtonGroup>
  );
}
