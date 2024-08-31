// src/services/api.ts

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api/v1';

export const processMessage = async (message: string, context: any) => {
  try {
    console.log('Processing message:', message);
    const response = await axios.post(`${API_BASE_URL}/process`, { 
      text: message,
      context: context
    }, {
      withCredentials: true
    });
    console.log('NLP response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error processing message:', error);
    if (axios.isAxiosError(error) && error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
      throw new Error(error.response.data.message || 'An error occurred while processing your request');
    }
    throw new Error('An unknown error occurred');
  }
};

// Mock login function
export const loginUser = async (personnelNumber: string, password: string) => {
  console.log('Attempting login for personnel number:', personnelNumber);
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Mock login logic
  if (personnelNumber === '12345' && password === 'password') {
    console.log('Login successful');
    return {
      token: 'mock-jwt-token',
      user: {
        personnelNumber: '12345',
        name: 'Mehmet Copur'
      }
    };
  } else {
    console.error('Login failed: Invalid credentials');
    throw new Error('Invalid credentials');
  }
};

export const fetchSAPData = async (endpoint: string, params: any): Promise<any> => {
  // Mevcut SAP veri çekme implementasyonunuz
  console.log('Fetching SAP data from:', endpoint, 'with params:', params);
  // API çağrısı yapılacak
  throw new Error('SAP data fetching not implemented');
};

export const sendMessageToNLP = processMessage;