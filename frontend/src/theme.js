import { createTheme } from '@mui/material/styles'
export default createTheme({
  palette: { mode:'dark', primary:{ main:'#60a5fa' }, background:{ default:'#0b0d10', paper:'#0f141a' } },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: { styleOverrides:{ root:{ textTransform:'none', borderRadius:12 } } },
    MuiPaper:  { styleOverrides:{ root:{ borderRadius:16 } } },
  }
})
