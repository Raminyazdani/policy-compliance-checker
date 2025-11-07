import { Typography } from '@mui/material'
export default function Heading({ children, level=2 }) {
  const variant = {1:'h4',2:'h5',3:'h6'}[level] || 'h6'
  return <Typography variant={variant} sx={{ mb:2 }}>{children}</Typography>
}
