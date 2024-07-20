import { sendMessageToNLP } from './api';

interface NLPResponse {
  reply: string;
  action?: {
    type: string;
    params: Record<string, any>;
  };
  context?: Record<string, any>;
}

let conversationContext: Record<string, any> = {};

export const processMessage = async (message: string): Promise<NLPResponse> => {
  try {
    console.log('Processing message:', message);
    console.log('Current context:', conversationContext);
    
    const response = await sendMessageToNLP(message, conversationContext);
    
    console.log('NLP service response:', response);
    
    conversationContext = { ...conversationContext, ...response.context };
    
    console.log('Updated context:', conversationContext);
    
    return response;
  } catch (error) {
    console.error('Error processing message:', error);
    throw new Error('Failed to process message');
  }
}

export const resetContext = () => {
  console.log('Resetting conversation context');
  conversationContext = {};
}