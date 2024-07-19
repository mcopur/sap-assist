import React from 'react';
import { Box, Paper, CircularProgress } from '@mui/material';
import MessageList from './MessageList';
import UserInput from './UserInput';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { sendMessage } from '../store/chatSlice';

const ChatInterface: React.FC = () => {
  const dispatch = useDispatch();
  const { messages, status } = useSelector((state: RootState) => state.chat);

  const handleSendMessage = (message: string) => {
    dispatch(sendMessage(message));
  };

  return (
    <Paper elevation={3} sx={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
        <MessageList messages={messages} />
        {status === 'loading' && (
          <Box display="flex" justifyContent="center" mt={2}>
            <CircularProgress />
          </Box>
        )}
      </Box>
      <UserInput onSendMessage={handleSendMessage} disabled={status === 'loading'} />
    </Paper>
  );
};

export default ChatInterface;