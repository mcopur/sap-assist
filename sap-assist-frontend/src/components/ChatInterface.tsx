import React, { useState, useEffect, useRef } from 'react';
import { Box, TextField, Button, Paper, Typography } from '@mui/material';
import { processMessage } from '../services/api';

interface Message {
  text: string;
  isUser: boolean;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [context, setContext] = useState({});
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    setMessages(prevMessages => [...prevMessages, { text: input, isUser: true }]);
    setInput('');

    try {
      const response = await processMessage(input, context);
      setMessages(prevMessages => [...prevMessages, { text: response.response, isUser: false }]);
      setContext(response.context);
    } catch (error) {
      console.error('Error processing message:', error);
      setMessages(prevMessages => [...prevMessages, { text: 'An error occurred. Please try again.', isUser: false }]);
    }
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Paper elevation={3} sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
        {messages.map((message, index) => (
          <Box key={index} sx={{ mb: 2, display: 'flex', justifyContent: message.isUser ? 'flex-end' : 'flex-start' }}>
            <Paper elevation={1} sx={{ p: 1, maxWidth: '70%', bgcolor: message.isUser ? 'primary.light' : 'secondary.light' }}>
              <Typography>{message.text}</Typography>
            </Paper>
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Paper>
      <Box sx={{ p: 2, bgcolor: 'background.default' }}>
        <TextField
          fullWidth
          variant="outlined"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Type your message here..."
        />
        <Button variant="contained" onClick={handleSendMessage} sx={{ mt: 1 }}>
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default ChatInterface;