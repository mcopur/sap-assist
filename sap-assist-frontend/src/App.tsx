// src/App.tsx
import React from 'react';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { Provider } from 'react-redux';
import { useSelector } from 'react-redux';
import theme from './styles/theme';
import { store, RootState } from './store';
import Header from './components/Header';
import ChatInterface from './components/ChatInterface';
import Login from './components/Login';
import ErrorBoundary from './components/ErrorBoundary';

const AppContent: React.FC = () => {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw' }}>
      <Header />
      <Box sx={{ flexGrow: 1, display: 'flex', overflow: 'hidden' }}>
        {isAuthenticated ? <ChatInterface /> : <Login />}
      </Box>
    </Box>
  );
};

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <ErrorBoundary>
          <AppContent />
        </ErrorBoundary>
      </ThemeProvider>
    </Provider>
  );
};

export default App;