import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';

import { log } from '@/logger';
import { LoadingState } from './index';

const logger = log.getLogger(`${LoadingState.name}_tests`);

describe('LoadingState', () => {
  afterEach(() => {
    cleanup();
  });

  it('should render correctly', () => {
    render(<LoadingState />);

    expect(screen.getByLabelText('Loading...')).toBeVisible();
  });

  it('should receive props correctly', () => {
    render(
      <LoadingState className="test-class" aria-label="A loading spinner">
        Loading some stuff
      </LoadingState>,
    );

    const loadingSpinner = screen.getByLabelText('A loading spinner');
    expect(loadingSpinner).toBeVisible();
    expect(loadingSpinner).toHaveClass('test-class');
    expect(loadingSpinner).toHaveAttribute('aria-label', 'A loading spinner');
  });
});
