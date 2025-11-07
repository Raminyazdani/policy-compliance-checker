import * as React from 'react';
import { Button, Snackbar, Alert, Checkbox, FormControlLabel } from '@mui/material';
import Section from '../../components/layout/Section';
import Heading from '../../components/layout/Heading';
import ToolbarX from '../../components/layout/Toolbar';
import DataTable from '../../components/table/DataTable';
import PolicyForm from './PolicyForm';
import { usePolicies } from './policies.store';
import { policiesApi } from './policies.api';

export default function PoliciesPanel() {
  const { items, refresh, createOne, updateOne, deleteOne, error } = usePolicies();
  const [open, setOpen] = React.useState(false);
  const [edit, setEdit] = React.useState(null);
  const [toast, setToast] = React.useState({ open:false, msg:'', severity:'success' });
  const fileRef = React.useRef(null);
  const [clearBefore, setClearBefore] = React.useState(false); // ← NEW

  React.useEffect(() => { refresh(); }, []);

  const onPickFile = () => fileRef.current?.click();
  const onUpload = async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    try {
      await policiesApi.upload(f, clearBefore); // ← pass clear flag
      await refresh();
      setToast({ open:true, msg:`Uploaded ${f.name}`, severity:'success' });
    } catch (err) {
      setToast({ open:true, msg: err.message || 'Upload failed', severity:'error' });
    } finally {
      e.target.value = '';
    }
  };

  return (
    <Section>
      <ToolbarX>
        <Heading>Policies</Heading>
        <div style={{ display:'flex', gap: 8, alignItems:'center' }}>
          <FormControlLabel
            control={<Checkbox checked={clearBefore} onChange={e=>setClearBefore(e.target.checked)} />}
            label="Clear table before import"
          />
          <input ref={fileRef} type="file" accept=".json,.csv" style={{ display:'none' }} onChange={onUpload}/>
          <Button variant="outlined" onClick={onPickFile}>Upload JSON/CSV</Button>
          <Button variant="contained" onClick={() => { setEdit(null); setOpen(true); }}>
            New Policy
          </Button>
        </div>
      </ToolbarX>

      <DataTable
        rows={items}
        getRowId={(r, i) => r.policy_id ?? r.id ?? `${i}`}
        columnOptions={{
          order: ['policy_id','field','operator','value','description'],
          labels: { policy_id: 'Policy ID' },
          actions: {
            render: (p) => (
              <>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => { setEdit(p.row); setOpen(true); }}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="error"
                  variant="outlined"
                  sx={{ ml: 1 }}
                  onClick={async () => {
                    const key = p.row.policy_id ?? p.row.id;
                    if (!key) return;
                    if (!confirm(`Delete ${key}?`)) return;
                    await deleteOne(key);
                    setToast({ open:true, msg:'Deleted', severity:'success' });
                  }}
                >
                  Delete
                </Button>
              </>
            )
          }
        }}
      />

      <PolicyForm
        open={open}
        initial={edit}
        onClose={() => setOpen(false)}
        onSave={async (payload) => {
          if (!payload.policy_id) return;
          if (edit) await updateOne(payload.policy_id, payload);
          else      await createOne(payload);
          setOpen(false);
          setToast({ open:true, msg: edit ? 'Updated' : 'Created', severity:'success' });
        }}
      />

      <Snackbar open={!!error || toast.open} autoHideDuration={2500} onClose={() => setToast({ ...toast, open:false })}>
        <Alert severity={error ? 'error' : toast.severity} variant="filled">
          {error || toast.msg}
        </Alert>
      </Snackbar>
    </Section>
  );
}
