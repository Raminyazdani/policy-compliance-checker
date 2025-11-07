import { Stack } from '@mui/material'
export default function ToolbarX({ children }) {
  return <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb:2 }}>{children}</Stack>
}
