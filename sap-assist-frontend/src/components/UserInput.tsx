// sap-assist-frontend/src/components/UserInput.tsx
import React, { useState } from 'react';
import { Box, TextField, IconButton } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

interface UserInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const UserInput: React.FC<UserInputProps> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ p: 2, backgroundColor: 'background.default' }}>
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Type your message here..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        disabled={disabled}
        InputProps={{
          endAdornment: (
            <IconButton type="submit" color="primary" disabled={disabled}>
              <SendIcon />
            </IconButton>
          ),
        }}
      />
    </Box>
  );
};

export default UserInput;