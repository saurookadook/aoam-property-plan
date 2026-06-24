import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';

import { log } from '@/logger';
import { AnchorLink } from './index';

const logger = log.getLogger(`${AnchorLink.name}_tests`);

describe('AnchorLink', () => {
  afterEach(() => {
    cleanup();
  });

  it('should render correctly', () => {
    render(<AnchorLink href="#test">Test</AnchorLink>);

    expect(screen.getByText('Test')).toBeVisible();
  });

  it('should receive props correctly', () => {
    render(
      <AnchorLink href="#test" className="test-class" aria-label="Test link">
        Test
      </AnchorLink>,
    );

    const link = screen.getByLabelText('Test link');
    expect(link).toBeVisible();
    expect(link).toHaveAttribute('href', '#test');
    expect(link).toHaveClass('test-class');
    expect(link).toHaveAttribute('aria-label', 'Test link');
  });
});
