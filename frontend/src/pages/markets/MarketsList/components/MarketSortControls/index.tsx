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
    <form id="market-sort-controls">
      <fieldset form="market-sort-controls">
        <legend id="market-sort-controls-label">Sort markets by:</legend>

        <ToggleButtonGroup
          aria-labelledby="market-sort-controls-label"
          className="market-sort-controls-btn-group"
          color="primary"
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
      </fieldset>
    </form>
  );
}
