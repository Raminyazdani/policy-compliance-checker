import * as React from 'react'
import { Dialog, DialogTitle, DialogContent, DialogActions, Stack, TextField, Checkbox, FormControlLabel, Button } from '@mui/material'
const empty = { username:'', name:'', lastname:'', email:'', role:'', password:'', mfa_enabled:0, login_count:0, age_days:0, age:18, income:0 }
export default function UserForm({ open, onClose, onSave, initial }) {
  const [form,setForm] = React.useState(initial || empty)
  React.useEffect(()=>{ setForm(initial || empty) },[initial,open])
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>{initial?'Edit User':'Create User'}</DialogTitle>
      <DialogContent sx={{ pt:2 }}>
        <Stack spacing={2}>
          <TextField label="Username" value={form.username} onChange={e=>setForm({...form, username:e.target.value})} required/>
          <TextField label="Name" value={form.name} onChange={e=>setForm({...form, name:e.target.value})}/>
          <TextField label="Lastname" value={form.lastname} onChange={e=>setForm({...form, lastname:e.target.value})}/>
          <TextField label="Email" value={form.email} onChange={e=>setForm({...form, email:e.target.value})}/>
          <TextField label="Role" value={form.role} onChange={e=>setForm({...form, role:e.target.value})}/>
          <TextField label="Password" type="password" value={form.password||''} onChange={e=>setForm({...form, password:e.target.value})}/>
          <FormControlLabel control={<Checkbox checked={!!form.mfa_enabled} onChange={e=>setForm({...form, mfa_enabled:e.target.checked})}/>} label="MFA enabled"/>
          <Stack direction="row" spacing={2}>
            <TextField label="Login count" type="number" value={form.login_count} onChange={e=>setForm({...form, login_count:e.target.value})}/>
            <TextField label="Age days" type="number" value={form.age_days} onChange={e=>setForm({...form, age_days:e.target.value})}/>
            <TextField label="Age" type="number" value={form.age} onChange={e=>setForm({...form, age:e.target.value})}/>
            <TextField label="Income" type="number" value={form.income} onChange={e=>setForm({...form, income:e.target.value})}/>
          </Stack>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={()=>onSave({
          ...form,
          mfa_enabled: form.mfa_enabled ? 1 : 0,
          login_count: Number(form.login_count||0),
          age_days: Number(form.age_days||0),
          age: Number(form.age||0),
          income: Number(form.income||0),
        })}>Save</Button>
      </DialogActions>
    </Dialog>
  )
}
