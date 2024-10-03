import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000'; 

export const processMessage = async (message: string, context: any) => {
  try {
    console.log('Processing message:', message);
    const response = await axios.post(`${API_BASE_URL}/classify`, { 
      text: message,
      context: context
    }, {
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    console.log('NLP response:', response.data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      console.error('Error processing message:', error);
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
      if (error.response.status === 429) {
        throw new Error('Çok fazla istek gönderildi. Lütfen biraz bekleyin ve tekrar deneyin.');
      } else if (error.response.status === 500) {
        throw new Error('Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin.');
      }
      throw new Error(error.response.data.error || 'Bir hata oluştu');
    }
    throw new Error('Bilinmeyen bir hata oluştu');
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