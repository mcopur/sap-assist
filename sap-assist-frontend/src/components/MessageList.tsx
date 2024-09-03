import React from 'react';
import { List, ListItem, ListItemText, Paper, Typography, Avatar } from '@mui/material';
import { Message } from '../types';

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <List>
      {messages.map((message, index) => (
        <ListItem key={index} sx={{ display: 'flex', justifyContent: message.isUser ? 'flex-end' : 'flex-start' }}>
          {!message.isUser && (
            <Avatar sx={{ bgcolor: 'primary.main', mr: 1 }}>AI</Avatar>
          )}
          <Paper 
            elevation={1} 
            sx={{ 
              p: 2, 
              maxWidth: '70%',
              bgcolor: message.isUser ? 'primary.light' : 'secondary.light',
              borderRadius: message.isUser ? '20px 20px 0 20px' : '20px 20px 20px 0',
            }}
          >
            <Typography variant="body1">{message.text}</Typography>
          </Paper>
          {message.isUser && (
            <Avatar sx={{ bgcolor: 'secondary.main', ml: 1 }}>U</Avatar>
          )}
        </ListItem>
      ))}
    </List>
  );
};

export default MessageList;