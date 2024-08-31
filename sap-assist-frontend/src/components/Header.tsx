// src/components/Header.tsx

import React from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { useDispatch } from 'react-redux';
import { logout } from '../store/authSlice';
import { AppDispatch } from '../store';

const Header: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" style={{ flexGrow: 1 }}>SAP Assist</Typography>
        <Button color="inherit" onClick={handleLogout}>Logout</Button>
      </Toolbar>
    </AppBar>
  );
};

export default Header;