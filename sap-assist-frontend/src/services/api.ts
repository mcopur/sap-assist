// src/services/api.ts
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api/v1';

// Mock login function
export const loginUser = async (personnelNumber: string, password: string) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Mock login logic
  if (personnelNumber === '12345' && password === 'password') {
    return {
      token: 'mock-jwt-token',
      user: {
        personnelNumber: '12345',
        name: 'John Doe'
      }
    };
  } else {
    throw new Error('Invalid credentials');
  }
};

export const sendMessageToNLP = async (message: string, context: any, token: string) => {
  try {
    console.log('Sending message to NLP:', message);
    const response = await axios.post(`${API_BASE_URL}/classify`, { 
      text: message,
      start_date: context.start_date || '',
      end_date: context.end_date || ''
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      },
      withCredentials: true
    });
    console.log('NLP response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error sending message to NLP:', error);
    if (axios.isAxiosError(error) && error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
      throw new Error(error.response.data.message || 'An error occurred while processing your request');
    }
    throw new Error('An unknown error occurred');
  }
};

export const sendLeaveRequest = async (token: string, startDate: string, endDate: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/leave-requests`, {
      start_date: startDate,
      end_date: endDate
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error sending leave request:', error);
    throw new Error('Failed to send leave request');
  }
};

export const getPurchaseRequests = async (token: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/purchase-requests`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching purchase requests:', error);
    throw new Error('Failed to fetch purchase requests');
  }
};

export const createPurchaseRequest = async (token: string, itemName: string, quantity: number) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/purchase-requests`, {
      item_name: itemName,
      quantity: quantity
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error creating purchase request:', error);
    throw new Error('Failed to create purchase request');
  }
};