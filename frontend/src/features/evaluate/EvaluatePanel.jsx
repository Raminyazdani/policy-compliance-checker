import * as React from 'react';
import { Button, Stack, Autocomplete, TextField, Checkbox } from '@mui/material';
import Section from '../../components/layout/Section';
import Heading from '../../components/layout/Heading';
import ToolbarX from '../../components/layout/Toolbar';
import DataTable from '../../components/table/DataTable';
import { useEvaluate } from './evaluate.store';

function exportCSV(rows, filename = 'evaluate.csv') {
  if (!rows?.length) return;
  const cols = Array.from(
    rows.reduce((s, r) => { Object.keys(r).forEach(k => s.add(k)); return s; }, new Set())
  );
  const esc = (v) => {
    if (v === null || v === undefined) return '';
    const s = typeof v === 'object' ? JSON.stringify(v) : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g,'""')}"` : s;
    };
  const lines = [
    cols.join(','),
    ...rows.map(r => cols.map(c => esc(r[c])).join(',')),
  ];
  const blob = new Blob([lines.join('\n')], { type:'text/csv;charset=utf-8;' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

export default function EvaluatePanel() {
  const { rows, refresh } = useEvaluate();

  const flatRows = React.useMemo(() => {
    if (!Array.isArray(rows)) return [];
    const out = [];
    for (const r of rows) {
      const username = r?.username ?? '<unknown>';
      for (const c of (r?.checks ?? [])) {
        out.push({ username, ...c });
      }
    }
    return out;
  }, [rows]);

  const policyOptions = React.useMemo(
    () => Array.from(new Set(flatRows.map(x => x.policy_id ?? x.id))).filter(Boolean).sort(),
    [flatRows]
  );
  const userOptions = React.useMemo(
    () => Array.from(new Set(flatRows.map(x => x.username))).filter(Boolean).sort(),
    [flatRows]
  );

  const [selPolicies, setSelPolicies] = React.useState([]);
  const [selUsers, setSelUsers] = React.useState([]);

  const filteredRows = React.useMemo(() => {
    return flatRows.filter(r => {
      const polKey = r.policy_id ?? r.id;
      const okPol = selPolicies.length ? selPolicies.includes(polKey) : true;
      const okUsr = selUsers.length ? selUsers.includes(r.username) : true;
      return okPol && okUsr;
    });
  }, [flatRows, selPolicies, selUsers]);

  return (
    <Section>
      <ToolbarX>
        <Heading>Evaluate — All Checks</Heading>

        <Stack direction="row" spacing={2} sx={{ flex: 1, justifyContent: 'flex-end', alignItems: 'center' }}>
          <Autocomplete
            multiple
            disableCloseOnSelect
            options={policyOptions}
            value={selPolicies}
            onChange={(_, v) => setSelPolicies(v)}
            size="small"
            sx={{ minWidth: 280 }}
            renderOption={(props, option, { selected }) => {
              // prevent React key warning by not spreading the "key" prop
              const { key, ...optionProps } = props;
              return (
                <li key={key} {...optionProps}>
                  <Checkbox checked={selected} sx={{ mr: 1 }} />
                  {option}
                </li>
              );
            }}
            renderInput={(params) => <TextField {...params} label="Filter by Policy" placeholder="Select policies" />}
          />

          <Autocomplete
            multiple
            disableCloseOnSelect
            options={userOptions}
            value={selUsers}
            onChange={(_, v) => setSelUsers(v)}
            size="small"
            sx={{ minWidth: 240 }}
            renderOption={(props, option, { selected }) => {
              // prevent React key warning by not spreading the "key" prop
              const { key, ...optionProps } = props;
              return (
                <li key={key} {...optionProps}>
                  <Checkbox checked={selected} sx={{ mr: 1 }} />
                  {option}
                </li>
              );
            }}
            renderInput={(params) => <TextField {...params} label="Filter by User" placeholder="Select users" />}
          />

          <Button variant="outlined" onClick={() => { setSelPolicies([]); setSelUsers([]); }}>
            Clear
          </Button>
          <Button variant="outlined" onClick={() => exportCSV(filteredRows)}>Export CSV</Button>
          <Button variant="contained" onClick={refresh}>Refresh</Button>
        </Stack>
      </ToolbarX>

      <DataTable
        rows={filteredRows}
        getRowId={(r, i) => `${r.username}-${(r.policy_id ?? r.id) ?? 'p'}-${r.field ?? ''}-${i}`}
        columnOptions={{ render: { passed: (p) => (p.value ? '✓' : '✗') } }}
        height={600}
      />
    </Section>
  );
}
