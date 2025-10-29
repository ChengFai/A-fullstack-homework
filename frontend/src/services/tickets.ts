import { api } from './http';

export async function getTickets() {
  const { data } = await api.get('/tickets/');
  return data;
}

export async function createTicket(body: {
  spent_at: string;
  amount: number;
  currency: string;
  description?: string;
  link?: string;
}) {
  const { data } = await api.post('/tickets/', body);
  return data;
}

export async function approveTicket(id: string) {
  const { data } = await api.post(`/tickets/${id}/approve`);
  return data;
}

export async function denyTicket(id: string) {
  const { data } = await api.post(`/tickets/${id}/deny`);
  return data;
}

export async function deleteTicket(id: string) {
  const { data } = await api.delete(`/tickets/${id}`);
  return data;
}
