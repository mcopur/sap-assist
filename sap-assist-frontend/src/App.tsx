import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from './store';
import { ThemeProvider, createTheme, CssBaseline, AppBar, Toolbar, Typography, Avatar, Button, Box } from '@mui/material';
import { blue, grey } from '@mui/material/colors';
import ChatInterface from './components/ChatInterface';

const theme = createTheme({
  palette: {
    primary: {
      main: blue[700],
    },
    secondary: {
      main: grey[300],
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 3px 10px rgba(0,0,0,0.08)',
        },
      },
    },
  },
});

const App: React.FC = () => {
  const auth = useSelector((state: RootState) => state.auth);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              SAP Assist
            </Typography>
            {auth.isAuthenticated && auth.user && (
              <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                <Avatar sx={{ width: 32, height: 32, mr: 1 }}>{auth.user.name[0]}</Avatar>
                <Typography variant="body2">{auth.user.name}</Typography>
              </Box>
            )}
            <Button color="inherit">
              {auth.isAuthenticated ? 'Logout' : 'Login'}
            </Button>
          </Toolbar>
        </AppBar>
        <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
          <ChatInterface />
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default App;