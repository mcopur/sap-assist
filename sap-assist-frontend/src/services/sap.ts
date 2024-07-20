import { fetchSAPData } from './api';

export const getLeaveBalance = async (employeeId: string) => {
  return await fetchSAPData('leave-balance', { employeeId });
};

export const submitLeaveRequest = async (employeeId: string, startDate: string, endDate: string, leaveType: string) => {
  return await fetchSAPData('submit-leave', { employeeId, startDate, endDate, leaveType });
};

export const getPurchaseRequests = async (employeeId: string) => {
  return await fetchSAPData('purchase-requests', { employeeId });
};

export const submitPurchaseRequest = async (employeeId: string, items: Array<{ name: string, quantity: number }>) => {
  return await fetchSAPData('submit-purchase', { employeeId, items });
};