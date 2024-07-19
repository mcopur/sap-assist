import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Message } from '../types';
import { sendMessageToNLP, fetchSAPData } from '../services/api';

interface ChatState {
  messages: Message[];
  status: 'idle' | 'loading' | 'failed';
}

const initialState: ChatState = {
  messages: [],
  status: 'idle',
};

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message: string, { dispatch }) => {
    const nlpResponse = await sendMessageToNLP(message);
    
    if (nlpResponse.action) {
      const sapData = await dispatch(performSAPAction(nlpResponse.action)).unwrap();
      return `${nlpResponse.reply}\n\nHere's the data from SAP: ${JSON.stringify(sapData)}`;
    }
    
    return nlpResponse.reply;
  }
);

export const performSAPAction = createAsyncThunk(
  'chat/performSAPAction',
  async (action: { type: string; params: object }) => {
    return await fetchSAPData(action.type, action.params);
  }
);

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(sendMessage.fulfilled, (state, action: PayloadAction<string>) => {
        state.status = 'idle';
        state.messages.push({ text: action.meta.arg, isUser: true });
        state.messages.push({ text: action.payload, isUser: false });
      })
      .addCase(sendMessage.rejected, (state) => {
        state.status = 'failed';
        state.messages.push({ text: "Sorry, I couldn't process your request. Please try again.", isUser: false });
      });
  },
});

export default chatSlice.reducer;