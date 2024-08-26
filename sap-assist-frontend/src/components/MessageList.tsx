import React from 'react';
import { List, ListItem, ListItemText, Paper, Typography } from '@mui/material';
import { styled } from '@mui/system';
import { Person, Android } from '@mui/icons-material';
import { Message } from '../types';

interface MessageListProps {
  messages: Message[];
}

const MessageBubble = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'isUser',
})<{ isUser: boolean }>(({ theme, isUser }) => ({
  padding: theme.spacing(2),
  maxWidth: '70%',
  display: 'flex',
  alignItems: 'center',
  borderRadius: isUser ? '20px 20px 0 20px' : '20px 20px 20px 0',
  backgroundColor: isUser ? theme.palette.primary.light : theme.palette.background.paper,
  border: isUser ? 'none' : `1px solid ${theme.palette.divider}`,
  alignSelf: isUser ? 'flex-end' : 'flex-start',
  boxShadow: theme.shadows[1],
  animation: 'fadeIn 0.3s ease-out',
  '@keyframes fadeIn': {
    from: { opacity: 0, transform: 'translateY(10px)' },
    to: { opacity: 1, transform: 'translateY(0)' },
  },
}));

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <List>
      {messages.map((message, index) => (
        <ListItem key={index} sx={{ display: 'flex', justifyContent: message.isUser ? 'flex-end' : 'flex-start' }}>
          <MessageBubble isUser={message.isUser}>
            {message.isUser ? <Person sx={{ mr: 1 }} /> : <Android sx={{ mr: 1 }} />}
            <ListItemText
              primary={message.text}
              secondary={
                <>
                  <Typography variant="caption" display="block">
                    {new Date(message.timestamp || Date.now()).toLocaleTimeString()}
                  </Typography>
                  {message.intent && (
                    <Typography variant="caption" display="block" color="textSecondary">
                      Intent: {message.intent}
                    </Typography>
                  )}
                </>
              }
            />
          </MessageBubble>
        </ListItem>
      ))}
    </List>
  );
};

export default MessageList;