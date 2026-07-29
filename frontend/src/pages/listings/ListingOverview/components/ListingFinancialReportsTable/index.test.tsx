import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, within } from '@testing-library/react';

import { log } from '@/logger';
import type { ListingFinancialReportEntity } from '@/types';
import { ListingFinancialReportsTable } from './index';

const logger = log.getLogger(`${ListingFinancialReportsTable.name}_tests`);

const baseReport: ListingFinancialReportEntity = {
  id: 'a1b2c3d4-e5f6-4789-a012-3456789abcde',
  created_at: '2024-01-01T00:00:00.000Z',
  updated_at: '2024-01-01T00:00:00.000Z',
  number_of_reviews: 12,
  rating_overall: 4.5,
  ttm_revenue: 25000,
  ttm_occupancy_rate: 0.75,
};

const secondReport: ListingFinancialReportEntity = {
  ...baseReport,
  id: 'b2c3d4e5-f6a7-4890-b123-456789abcdef',
  number_of_reviews: 3,
  rating_overall: 3.9,
  ttm_revenue: 12000,
  ttm_occupancy_rate: 0.6,
};

describe('ListingFinancialReportsTable', () => {
  afterEach(() => {
    cleanup();
  });

  it('should render correctly', () => {
    const { container } = render(
      <ListingFinancialReportsTable financialReports={[baseReport]} />,
    );

    const wrapper = container.querySelector(
      '.listing-overview-data__financial-reports__table',
    ) as HTMLElement;
    expect(wrapper).toBeVisible();

    const table = wrapper.querySelector('table') as HTMLTableElement;
    expect(table).toBeVisible();
  });

  it('should render a column header for each key on the financial report', () => {
    const { container } = render(
      <ListingFinancialReportsTable financialReports={[baseReport]} />,
    );

    const headerRow = container.querySelector('thead tr') as HTMLElement;
    const headerCells = within(headerRow).getAllByRole('columnheader');

    expect(headerCells).toHaveLength(Object.keys(baseReport).length);
    for (const key of Object.keys(baseReport)) {
      expect(within(headerRow).getByText(key)).toBeVisible();
    }
  });

  it('should render a row for each financial report with the correct values', () => {
    const { container } = render(
      <ListingFinancialReportsTable
        financialReports={[baseReport, secondReport]}
      />,
    );

    const bodyRows = container.querySelectorAll('tbody tr');
    expect(bodyRows).toHaveLength(2);

    const firstRowCells = within(bodyRows[0] as HTMLElement).getAllByRole('cell');
    expect(firstRowCells.map((cell) => cell.textContent)).toEqual(
      Object.values(baseReport).map(String),
    );

    const secondRowCells = within(bodyRows[1] as HTMLElement).getAllByRole('cell');
    expect(secondRowCells.map((cell) => cell.textContent)).toEqual(
      Object.values(secondReport).map(String),
    );
  });

  it('should render an empty table with no headers or rows when there are no financial reports', () => {
    const { container } = render(
      <ListingFinancialReportsTable financialReports={[]} />,
    );

    expect(container.querySelectorAll('thead th')).toHaveLength(0);
    expect(container.querySelectorAll('tbody tr')).toHaveLength(0);
  });
});
