import { Chip, Tooltip } from '@mui/material';

import type { InvestmentFit } from '@/common/utils/investmentFit';
import { FlexRow } from '@/layouts';

import './styles.scss';

/**
 * `fit` is `null` for a market with no financial report - a fresh roster entry
 * has no score until the ingest cron has run, which is an ordinary state, not
 * an error.
 */
export function FitScoreBadge({ fit }: { fit: InvestmentFit | null }) {
  if (fit == null) {
    return (
      <Chip
        className="fit-score-badge fit-score-badge--pending"
        label="Fit score pending"
        size="small"
        variant="outlined"
      />
    );
  }

  return (
    <FlexRow className="fit-score-badge">
      <Tooltip title="A derived heuristic weighing revenue, occupancy, ADR and listing depth - not a datum from AirROI.">
        <Chip
          className="fit-score-badge__score"
          color="primary"
          label={`Fit ${fit.score}`}
          size="small"
        />
      </Tooltip>

      {fit.isThinMarket && (
        <Tooltip title="Fewer than 30 active listings - depth alone cannot tell 'no competition' from 'no market'.">
          <Chip
            className="fit-score-badge__thin-market"
            label={`Thin market (${Math.round(fit.listingCount ?? 0)} listings)`}
            size="small"
            variant="outlined"
          />
        </Tooltip>
      )}
    </FlexRow>
  );
}
