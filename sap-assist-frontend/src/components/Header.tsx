// src/components/Header.tsx

import React from 'react';
import { AppBar, Toolbar, Typography, Avatar, IconButton, Box } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';

const Header: React.FC = () => {
  return (
    <AppBar position="static" color="primary" elevation={0}>
      <Toolbar>
        <IconButton edge="start" color="inherit" aria-label="menu" sx={{ mr: 2 }}>
          <MenuIcon />
        </IconButton>
        <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
          SAP Assist
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography variant="body2" sx={{ mr: 2 }}>
            John Doe
          </Typography>
          <Avatar alt="User" src="/path-to-user-image.jpg" />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;