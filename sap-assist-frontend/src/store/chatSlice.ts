// src/store/chatSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { sendMessageToNLP } from '../services/api';
import { RootState } from './index';

interface Message {
  text: string;
  isUser: boolean;
  intent?: string;
  timestamp: number;
}

interface ChatState {
  messages: Message[];
  status: 'idle' | 'loading' | 'failed';
  error: string | null;
  context: {
    start_date?: string;
    end_date?: string;
    [key: string]: string | undefined;
  };
}

const initialState: ChatState = {
  messages: [],
  status: 'idle',
  error: null,
  context: {},
};

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message: string, { getState, dispatch }) => {
    const state = getState() as RootState;
    const token = state.auth.token;
    if (!token) {
      throw new Error('No authentication token available');
    }
    const context = state.chat.context;
    dispatch(chatSlice.actions.addMessage({ 
      text: message, 
      isUser: true, 
      timestamp: Date.now() 
    }));
    const response = await sendMessageToNLP(message, context, token);
    return response;
  }
);

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload);
    },
    resetChat: (state) => {
      state.messages = [];
      state.error = null;
      state.context = {};
    },
    updateContext: (state, action: PayloadAction<Record<string, string>>) => {
      state.context = { ...state.context, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.status = 'idle';
        state.messages.push({ 
          text: action.payload.response, 
          isUser: false, 
          intent: action.payload.intent,
          timestamp: Date.now()
        });
        state.context = { ...state.context, ...action.payload.context };
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Failed to send message';
        state.messages.push({ 
          text: "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.", 
          isUser: false, 
          intent: "error",
          timestamp: Date.now()
        });
      });
  },
});

export const { addMessage, resetChat, updateContext } = chatSlice.actions;

export default chatSlice.reducer;