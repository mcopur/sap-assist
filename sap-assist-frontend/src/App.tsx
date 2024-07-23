// src/App.tsx

import React from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Provider } from 'react-redux';
import theme from './theme';
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
          <Header />
          <ChatInterface />
        </ErrorBoundary>
      </ThemeProvider>
    </Provider>
  );
};

export default App;