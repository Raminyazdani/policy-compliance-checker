import { Stack } from '@mui/material'
export default function Row({ children, gap=2, ...rest }) { return <Stack direction="row" spacing={gap} flexWrap="wrap" {...rest}>{children}</Stack> }
