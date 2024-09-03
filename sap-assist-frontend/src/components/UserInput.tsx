import React, { useState, useRef, useEffect } from 'react';
import { Box, TextField, IconButton, useTheme, useMediaQuery } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

interface UserInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const UserInput: React.FC<UserInputProps> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ 
      display: 'flex',
      alignItems: 'center',
      backgroundColor: 'background.default' 
    }}>
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Type your message here..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        disabled={disabled}
        inputRef={inputRef}
        multiline
        maxRows={4}
        size={isMobile ? "small" : "medium"}
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: theme.shape.borderRadius,
            '&.Mui-focused': {
              boxShadow: `0 0 0 2px ${theme.palette.primary.main}`,
            },
          },
        }}
      />
      <IconButton 
        type="submit" 
        color="primary" 
        disabled={disabled || !message.trim()}
        size={isMobile ? "small" : "medium"}
        sx={{ ml: 1 }}
      >
        <SendIcon />
      </IconButton>
    </Box>
  );
};

export default UserInput;