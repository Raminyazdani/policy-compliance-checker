import * as React from 'react';
import { Button, Snackbar, Alert, Checkbox, FormControlLabel } from '@mui/material';
import Section from '../../components/layout/Section';
import Heading from '../../components/layout/Heading';
import ToolbarX from '../../components/layout/Toolbar';
import DataTable from '../../components/table/DataTable';
import { useUsers } from './users.store';
import { usersApi } from './users.api';

export default function UsersPanel() {
  const { items, refresh, createOne, updateOne, deleteOne, error } = useUsers();
  const [toast, setToast] = React.useState({ open:false, msg:'', severity:'success' });
  const fileRef = React.useRef(null);
  const [clearBefore, setClearBefore] = React.useState(false); // ← NEW

  React.useEffect(() => { refresh(); }, []);

  const onPickFile = () => fileRef.current?.click();
  const onUpload = async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    try {
      await usersApi.upload(f, clearBefore); // ← pass clear flag
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
        <Heading>Users</Heading>
        <div style={{ display:'flex', gap: 8, alignItems:'center' }}>
          <FormControlLabel
            control={<Checkbox checked={clearBefore} onChange={e=>setClearBefore(e.target.checked)} />}
            label="Clear table before import"
          />
          <input ref={fileRef} type="file" accept=".json,.csv" style={{ display:'none' }} onChange={onUpload}/>
          <Button variant="outlined" onClick={onPickFile}>Upload JSON/CSV</Button>
        </div>
      </ToolbarX>

      <DataTable
        rows={items}
        getRowId={(r, i) => r.user_id ?? r.id ?? r.username ?? `${i}`}
        columnOptions={{
          exclude: ['password'],
          labels: { mfa_enabled: 'MFA' },
        }}
        height={600}
      />

      <Snackbar open={!!error || toast.open} autoHideDuration={2500} onClose={() => setToast({ ...toast, open:false })}>
        <Alert severity={error ? 'error' : toast.severity} variant="filled">
          {error || toast.msg}
        </Alert>
      </Snackbar>
    </Section>
  );
}
