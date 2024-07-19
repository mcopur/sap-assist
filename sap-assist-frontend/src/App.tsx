import React from 'react';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { Provider } from 'react-redux';
import theme from './styles/theme';
import { store } from './store';
import Header from './components/Header';
import ChatInterface from './components/ChatInterface';
import ErrorBoundary from './components/ErrorBoundary';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <ErrorBoundary>
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
            <Header />
            <ChatInterface />
          </Box>
        </ErrorBoundary>
      </ThemeProvider>
    </Provider>
  );
};

export default App;