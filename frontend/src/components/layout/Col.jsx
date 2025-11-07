import { Box } from '@mui/material'
export default function Col({ children, basis=300, grow=1, ...rest }) {
  return <Box sx={{ flex: `${grow} 1 ${basis}px` }} {...rest}>{children}</Box>
}
