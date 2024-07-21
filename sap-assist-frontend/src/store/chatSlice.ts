// sap-assist-frontend/src/store/chatSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Message } from '../types';
import { sendMessageToNLP } from '../services/api';
import { RootState } from './index';

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
  async (message: string, { getState, rejectWithValue }) => {
    try {
      const state = getState() as RootState;
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
      return rejectWithValue(error instanceof Error ? error.message : 'An unknown error occurred');
    }
  }
);

export const resetChat = createAsyncThunk(
  'chat/resetChat',
  async (_, { dispatch }) => {
    dispatch(chatSlice.actions.clearMessages());
    dispatch(chatSlice.actions.updateContext({}));
  }
);

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
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
        state.messages.push({ text: action.meta.arg, isUser: true });
        state.messages.push({ text: action.payload.reply, isUser: false });
        state.context = action.payload.newContext;
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload as string;
        state.messages.push({ text: "Sorry, I couldn't process your request. Please try again.", isUser: false });
      })
      .addCase(resetChat.fulfilled, (state) => {
        state.messages = [];
        state.status = 'idle';
        state.error = null;
        state.context = {};
      });
  },
});

export const { clearMessages, updateContext } = chatSlice.actions;
export default chatSlice.reducer;