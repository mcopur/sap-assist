// src/store/chatSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { sendMessageToNLP } from '../services/api';
import { RootState } from './index';

interface ChatState {
  messages: Array<{ text: string; isUser: boolean }>;
  status: 'idle' | 'loading' | 'failed';
  error: string | null;
  context: {
    start_date?: string;
    end_date?: string;
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
    dispatch(chatSlice.actions.addMessage({ text: message, isUser: true }));
    const response = await sendMessageToNLP(message, context, token);
    return response;
  }
);

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    resetChat: (state) => {
      state.messages = [];
      state.error = null;
      state.context = {};
    },
    updateContext: (state, action) => {
      state.context = { ...state.context, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.status = 'idle';
        state.messages.push({ text: action.payload.response, isUser: false });
        state.context = { ...state.context, ...action.payload.context };
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Failed to send message';
      });
  },
});

export const { addMessage, resetChat, updateContext } = chatSlice.actions;

export default chatSlice.reducer;