import React from 'react';
import { List, ListItem, Paper, Typography, Avatar, Box } from '@mui/material';
import { Message } from '../types';

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <List>
      {messages.map((message, index) => (
        <ListItem key={index} sx={{ 
          display: 'flex', 
          justifyContent: message.isUser ? 'flex-end' : 'flex-start',
          mb: 2,
        }}>
          {!message.isUser && (
            <Avatar sx={{ bgcolor: 'primary.main', mr: 1 }}>AI</Avatar>
          )}
          <Box sx={{ maxWidth: '70%' }}>
            <Paper 
              elevation={0} 
              sx={{ 
                p: 2, 
                bgcolor: message.isUser ? 'primary.light' : 'background.paper',
                borderRadius: message.isUser ? '20px 20px 0 20px' : '20px 20px 20px 0',
                border: (theme) => `1px solid ${theme.palette.divider}`,
              }}
            >
              <Typography variant="body1">{message.text}</Typography>
            </Paper>
            <Typography variant="caption" sx={{ mt: 0.5, display: 'block', textAlign: message.isUser ? 'right' : 'left' }}>
              {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </Typography>
          </Box>
          {message.isUser && (
            <Avatar sx={{ bgcolor: 'secondary.main', ml: 1 }}>U</Avatar>
          )}
        </ListItem>
      ))}
    </List>
  );
};

export default MessageList;