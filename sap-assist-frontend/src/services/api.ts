import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api'; // Backend URL'inizi buraya yazın

export const sendMessageToNLP = async (message: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/chat`, { message });
    return response.data;
  } catch (error) {
    console.error('Error sending message to NLP:', error);
    throw error;
  }
};

export const fetchSAPData = async (endpoint: string, params: object) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/sap/${endpoint}`, { params });
    return response.data;
  } catch (error) {
    console.error(`Error fetching SAP data from ${endpoint}:`, error);
    throw error;
  }
};