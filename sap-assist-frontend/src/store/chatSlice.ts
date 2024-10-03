// sap-assist-frontend/src/store/chatSlice.ts

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { processMessage } from '../services/api';
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
  async (message: string, { dispatch, getState, rejectWithValue }) => {
    try {
      const state = getState() as RootState;
      dispatch(chatSlice.actions.addMessage({ text: message, isUser: true }));
      
      const context = state.chat.context;
      const response = await processMessage(message, context);
      
      if (!response || !response.intent) {
        throw new Error('Geçersiz yanıt alındı');
      }

      const newContext = { ...context, lastIntent: response.intent };
      
      return { 
        reply: response.response,
        newContext 
      };
    } catch (error) {
      console.error('Error in sendMessage:', error);
      let errorMessage = 'Bir hata oluştu. Lütfen tekrar deneyin.';
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      return rejectWithValue(errorMessage);
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
        const errorMessage = action.payload as string || 'Bilinmeyen bir hata oluştu';
        state.error = errorMessage;
        state.messages.push({ text: errorMessage, isUser: false });
      });
  },
});

export const resetChat = createAsyncThunk(
  'chat/resetChat',
  async (_, { dispatch }) => {
    dispatch(chatSlice.actions.clearMessages());
    dispatch(chatSlice.actions.updateContext({}));
  }
);

export const { addMessage, clearMessages, updateContext } = chatSlice.actions;
export default chatSlice.reducer;