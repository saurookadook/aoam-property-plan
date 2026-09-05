import { useMemo } from 'react';
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { Button, Tooltip, Typography } from '@mui/material';

import type { PropertyCompWithListingEntity } from '@/types';
import { useCurrency } from '@/providers';
import type { CurrencyRate } from '@/common/utils/currency';
import { FlexColumn, FlexRow } from '@/layouts';
import { formatReportAmount } from '../../utils';
import { useRefreshCompsMutation } from '../../../queries';

import './styles.scss';

const columnHelper = createColumnHelper<PropertyCompWithListingEntity>();

/**
 * `@tanstack/react-table` with `getSortedRowModel`, default revenue desc.
 * `ListingFinancialReportsTable` derives its columns from `Object.keys` and has
 * no sorting - that skeleton is not copied here; columns are declared
 * explicitly instead, the way a comp table with a defined shape should be.
 */
export function PropertyCompsTable({
  comps,
  propertyId,
  rate,
}: {
  comps: PropertyCompWithListingEntity[];
  propertyId: string;
  rate: CurrencyRate | null;
}) {
  const currency = useCurrency();
  const refreshMutation = useRefreshCompsMutation(propertyId);

  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => row.listing?.name ?? 'Unknown listing', {
        id: 'name',
        header: 'Name',
        cell: (info) => {
          const sourceUrl = info.row.original.listing?.source_url;
          return sourceUrl == null ? (
            info.getValue()
          ) : (
            <a href={sourceUrl} rel="noreferrer" target="_blank">
              {info.getValue()}
            </a>
          );
        },
      }),
      columnHelper.accessor((row) => row.listing?.property_type ?? '—', {
        id: 'propertyType',
        header: 'Type',
      }),
      columnHelper.accessor((row) => row.listing?.bedrooms ?? null, {
        id: 'bedrooms',
        header: 'Bedrooms',
        cell: (info) => info.getValue() ?? '—',
      }),
      columnHelper.accessor('adr_cop', {
        id: 'adr',
        header: 'ADR',
        cell: (info) => formatReportAmount(currency, rate, info.getValue()).text,
      }),
      columnHelper.accessor('occupancy_rate', {
        id: 'occupancy',
        header: 'Occupancy',
        cell: (info) => {
          const value = info.getValue();
          return value == null ? '—' : `${(value * 100).toFixed(0)}%`;
        },
      }),
      columnHelper.accessor('ttm_revenue_cop', {
        id: 'revenue',
        header: 'Est. annual revenue',
        cell: (info) => formatReportAmount(currency, rate, info.getValue()).text,
      }),
      columnHelper.accessor('distance_km', {
        id: 'distance',
        header: 'Distance',
        cell: (info) => {
          const value = info.getValue();
          return value == null ? '—' : `${value.toFixed(1)} km`;
        },
      }),
    ],
    [currency, rate],
  );

  const table = useReactTable({
    data: comps,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    initialState: {
      sorting: [{ id: 'revenue', desc: true }],
    },
  });

  return (
    <FlexColumn className="property-comps-table">
      <FlexRow className="property-comps-table__header">
        <Typography variant="h3">{`Comparable listings (${comps.length})`}</Typography>

        <Tooltip title="Spends a fresh AirROI call and replaces the cached comp set.">
          <span>
            <Button
              disabled={refreshMutation.isPending}
              size="small"
              variant="outlined"
              onClick={() => refreshMutation.mutate()}
            >
              Refresh comps
            </Button>
          </span>
        </Tooltip>
      </FlexRow>

      {comps.length === 0 ? (
        <Typography variant="body2">No comparable listings yet.</Typography>
      ) : (
        <table>
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    aria-sort={
                      header.column.getIsSorted() === 'asc'
                        ? 'ascending'
                        : header.column.getIsSorted() === 'desc'
                          ? 'descending'
                          : 'none'
                    }
                  >
                    <button
                      type="button"
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() === 'asc' && ' ▲'}
                      {header.column.getIsSorted() === 'desc' && ' ▼'}
                    </button>
                  </th>
                ))}
              </tr>
            ))}
          </thead>

          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </FlexColumn>
  );
}
