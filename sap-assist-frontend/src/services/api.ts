import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api/v1';

export const sendMessageToNLP = async (message: string, context: any) => {
  try {
    console.log('Sending message to NLP:', message);
    const response = await axios.post(`${API_BASE_URL}/classify`, { 
      text: message,
      start_date: context.start_date || '',
      end_date: context.end_date || ''
    }, {
      withCredentials: true
    });
    console.log('NLP response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error sending message to NLP:', error);
    if (axios.isAxiosError(error)) {
      console.error('Response data:', error.response?.data);
      console.error('Response status:', error.response?.status);
    }
    throw error;
  }
};