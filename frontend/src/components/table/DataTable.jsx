import React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { inferColumns } from './inferColumns';

const fallbackGetRowId = (r, idx) =>
  r?.policy_id ?? r?.user_id ?? r?.id ?? r?.username ?? `${idx}`;

export default function DataTable({
  rows = [],
  columns = [],
  columnOptions = {},
  getRowId,
  pageSize = 10,
  height = 520,
}) {
  const cols = columns.length ? columns : inferColumns(rows, columnOptions);

  return (
    <div style={{ height }}>
      <DataGrid
        rows={rows}
        columns={cols}
        getRowId={getRowId || fallbackGetRowId}
        disableRowSelectionOnClick
        pageSizeOptions={[pageSize, 25, 50]}
        initialState={{ pagination: { paginationModel: { pageSize } } }}
      />
    </div>
  );
}
