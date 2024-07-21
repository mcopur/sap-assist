// sap-assist-frontend/src/components/MessageList.tsx
import React from 'react';
import { List, ListItem, ListItemText, Paper } from '@mui/material';
import { Message } from '../types';

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <List>
      {messages.map((message, index) => (
        <ListItem key={index} sx={{ display: 'flex', justifyContent: message.isUser ? 'flex-end' : 'flex-start' }}>
          <Paper 
            elevation={1} 
            sx={{ 
              p: 2, 
              maxWidth: '70%',
              bgcolor: message.isUser ? 'primary.light' : 'secondary.light',
            }}
          >
            <ListItemText primary={message.text} />
          </Paper>
        </ListItem>
      ))}
    </List>
  );
};

export default MessageList;