// src/store/chatSlice.ts

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { sendMessageToNLP } from '../services/api';
import { RootState } from './index';
import { Message } from '../types';

interface ChatState {
  messages: Message[];
  status: 'idle' | 'loading' | 'failed';
  error: string | null;
  context: Record<string, any>;
}

const initialState: ChatState = {
  messages: [],
  status: 'idle',
  error: null,
  context: {},
};

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message: string, { dispatch, getState }) => {
    try {
      const state = getState() as RootState;
      dispatch(chatSlice.actions.addMessage({ text: message, isUser: true }));
      
      const context = state.chat.context;
      const response = await sendMessageToNLP(message, context);
      
      if (!response || !response.intent) {
        throw new Error('Invalid response from NLP service');
      }

      const newContext = { ...context, lastIntent: response.intent };
      
      return { 
        reply: response.response,
        newContext 
      };
    } catch (error) {
      console.error('Error in sendMessage:', error);
      return { 
        reply: "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.", 
        newContext: {} 
      };
    }
  }
);

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload);
    },
    clearMessages: (state) => {
      state.messages = [];
      state.error = null;
    },
    updateContext: (state, action: PayloadAction<Record<string, any>>) => {
      state.context = { ...state.context, ...action.payload };
    },
    resetChat: (state) => {
      state.messages = [];
      state.error = null;
      state.context = {};
      state.status = 'idle';
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
        state.messages.push({ text: action.payload.reply, isUser: false });
        state.context = action.payload.newContext;
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'An unknown error occurred';
        state.messages.push({ text: "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.", isUser: false });
      });
  },
});

export const { addMessage, clearMessages, updateContext, resetChat } = chatSlice.actions;
export default chatSlice.reducer;