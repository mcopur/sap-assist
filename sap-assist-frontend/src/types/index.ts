// sap-assist-frontend/src/types/index.ts
export interface Message {
  text: string;
  isUser: boolean;
  intent?: string;
  timestamp?: number;
}