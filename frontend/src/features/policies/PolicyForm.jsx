import React, { useEffect, useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Stack, TextField, MenuItem, Button } from '@mui/material';

const OPS = ['==','!=','>=','<=','>','<','in','includes'];

const coerce = (op, raw) => {
  const t = String(raw ?? '').trim();
  if (op === 'in') {
    if (t.startsWith('[')) { try { return JSON.parse(t); } catch {} }
    return t ? t.split(',').map(s => s.trim()) : [];
  }
  if (!Number.isNaN(Number(t)) && t !== '') return Number(t);
  if (t === 'true' || t === 'false') return t === 'true';
  return raw;
};

export default function PolicyForm({ open, onClose, onSave, initial }) {
  const empty = { policy_id:'', description:'', field:'', operator:'==', value:'' };
  const [form, setForm] = useState(initial || empty);

  useEffect(() => { setForm(initial || empty); }, [initial, open]);

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>{initial ? 'Edit Policy' : 'Create Policy'}</DialogTitle>
      <DialogContent sx={{ pt:2 }}>
        <Stack spacing={2}>
          <TextField
            label="Policy ID"
            value={form.policy_id}
            disabled={!!initial}
            onChange={e => setForm({ ...form, policy_id: e.target.value })}
            required
          />
          <TextField
            label="Field"
            value={form.field}
            onChange={e => setForm({ ...form, field: e.target.value })}
            required
          />
          <TextField
            select
            label="Operator"
            value={form.operator}
            onChange={e => setForm({ ...form, operator: e.target.value })}
          >
            {OPS.map(op => <MenuItem key={op} value={op}>{op}</MenuItem>)}
          </TextField>
          <TextField
            label='Value (e.g. 18 | "@acme.com" | ["admin","devops"])'
            value={form.value}
            onChange={e => setForm({ ...form, value: e.target.value })}
          />
          <TextField
            label="Description"
            value={form.description}
            onChange={e => setForm({ ...form, description: e.target.value })}
            multiline
            minRows={2}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={() => onSave({
            policy_id: (form.policy_id || '').trim(),
            description: form.description,
            field: form.field,
            operator: form.operator,
            value: coerce(form.operator, form.value)
          })}
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
}
