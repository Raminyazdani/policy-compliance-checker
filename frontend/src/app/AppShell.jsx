import { AppBar, Toolbar, Typography, Container, Paper, BottomNavigation, BottomNavigationAction, Tabs, Tab } from '@mui/material';
import PolicyIcon from '@mui/icons-material/Rule';
import PeopleIcon from '@mui/icons-material/People';
import CheckIcon from '@mui/icons-material/CheckCircle';

export default function AppShell({ navIndex, onNavChange, children }) {
  return (
    <>
      <AppBar position="sticky" color="transparent" elevation={0}
              sx={{ borderBottom:'1px solid #1f2937', backdropFilter:'blur(6px)' }}>
        <Toolbar sx={{ gap: 3 }}>
          <Typography variant="h6" sx={{ fontWeight:700, color:'#93c5fd' }}>Policy Compliance</Typography>

          <Tabs
            value={navIndex}
            onChange={(_, v) => onNavChange(v)}
            sx={{ ml: 2, display: { xs: 'none', md: 'flex' } }}
          >
            <Tab icon={<PolicyIcon sx={{ mr: 1 }} />} iconPosition="start" label="Policies" />
            <Tab icon={<PeopleIcon sx={{ mr: 1 }} />} iconPosition="start" label="Users" />
            <Tab icon={<CheckIcon sx={{ mr: 1 }} />} iconPosition="start" label="Evaluate" />
          </Tabs>
        </Toolbar>
      </AppBar>

      <Container sx={{ py: 3, pb: { xs: 9, md: 3 } }}>
        {children}
      </Container>

      <Paper sx={{ position:'fixed', bottom:0, left:0, right:0, display:{ xs:'block', md:'none'} }} elevation={8}>
        <BottomNavigation value={navIndex} onChange={(_, v) => onNavChange(v)} showLabels>
          <BottomNavigationAction label="Policies" icon={<PolicyIcon/>}/>
          <BottomNavigationAction label="Users" icon={<PeopleIcon/>}/>
          <BottomNavigationAction label="Evaluate" icon={<CheckIcon/>}/>
        </BottomNavigation>
      </Paper>
    </>
  );
}
