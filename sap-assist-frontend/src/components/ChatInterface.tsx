import React, { useRef, useEffect } from 'react';
import { Box, Paper, CircularProgress, Button } from '@mui/material';
import MessageList from './MessageList';
import UserInput from './UserInput';
import SuggestionChips from './SuggestionChips';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { sendMessage, resetChat } from '../store/chatSlice';

const ChatInterface: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { messages, status } = useSelector((state: RootState) => state.chat);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = (message: string) => {
    dispatch(sendMessage(message));
  };

  const handleResetChat = () => {
    dispatch(resetChat());
  };

  const suggestions = [
    "What's my leave balance?",
    "I want to request a leave",
    "Show my recent purchase requests",
    "How do I submit a new purchase request?"
  ];

  const handleSuggestionClick = (suggestion: string) => {
    dispatch(sendMessage(suggestion));
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
        <div ref={messagesEndRef} />
      </Box>
      <Box sx={{ p: 2, backgroundColor: 'background.default' }}>
        <SuggestionChips suggestions={suggestions} onSuggestionClick={handleSuggestionClick} />
        <Button variant="outlined" onClick={handleResetChat} sx={{ mb: 2 }}>
          Reset Chat
        </Button>
        <UserInput onSendMessage={handleSendMessage} disabled={status === 'loading'} />
      </Box>
    </Paper>
  );
};

export default ChatInterface;