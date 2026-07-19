import { useMemo } from 'react';
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';

import type { ListingFinancialReportEntity } from '@/types';
import { FlexRow } from '@/layouts';

import './styles.scss';

const columnHelper = createColumnHelper<ListingFinancialReportEntity>();

export function ListingFinancialReportsTable({
  financialReports,
}: {
  financialReports: ListingFinancialReportEntity[];
}) {
  const tableColumns = useMemo(() => {
    const columnHeaders =
      financialReports.length > 0 ? Object.keys(financialReports[0]) : [];
    return columnHeaders.map((headerKey) =>
      columnHelper.accessor(headerKey as keyof ListingFinancialReportEntity, {
        cell: (info) => info.getValue(),
        header: () => <span className={`column-header-${headerKey}`}>{headerKey}</span>,
      }),
    );
  }, [financialReports]);

  const financialReportsTable = useReactTable({
    data: financialReports,
    columns: tableColumns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <FlexRow className="listing-overview-data__financial-reports__table">
      <table>
        <thead>
          {financialReportsTable.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id}>
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>

        <tbody>
          {financialReportsTable.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id}>
                  {flexRender(
                    cell.column.columnDef.cell, // force formatting
                    cell.getContext(),
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </FlexRow>
  );
}
