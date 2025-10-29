import { api } from './http';

export async function getEmployees() {
  const { data } = await api.get('/employees/');
  return data;
}

export async function suspendEmployee(id: string) {
  const { data } = await api.post(`/employees/${id}/suspend`);
  return data;
}

export async function activateEmployee(id: string) {
  const { data } = await api.post(`/employees/${id}/activate`);
  return data;
}
