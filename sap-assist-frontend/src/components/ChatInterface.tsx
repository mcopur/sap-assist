import React, { useRef, useEffect } from 'react';
import { Box, CircularProgress, Button } from '@mui/material';
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

  useEffect(() => {
    console.log("Current messages state:", messages);
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    console.log("Sending message:", message);
    try {
      const resultAction = await dispatch(sendMessage(message));
      if (sendMessage.fulfilled.match(resultAction)) {
        console.log("Message sent successfully. Response:", resultAction.payload);
      } else if (sendMessage.rejected.match(resultAction)) {
        console.error("Failed to send message:", resultAction.error);
      }
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  const handleResetChat = () => {
    console.log("Resetting chat");
    dispatch(resetChat());
  };

  const suggestions = [
    "What's my leave balance?",
    "I want to request a leave",
    "Show my recent purchase requests",
    "How do I submit a new purchase request?"
  ];

  const handleSuggestionClick = (suggestion: string) => {
    console.log("Suggestion clicked:", suggestion);
    handleSendMessage(suggestion);
  };

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      width: '100%',
      overflow: 'hidden'
    }}>
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
    </Box>
  );
};

export default ChatInterface;