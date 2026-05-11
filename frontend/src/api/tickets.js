import { apiClient } from "./client";

export async function createTicket(payload) {
  const response = await apiClient.post("/tickets/", payload);
  return response.data.data;
}

export async function getMyTickets(params = {}) {
  const response = await apiClient.get("/tickets/my/", { params });
  return response.data.data;
}

export async function getManagerTickets(params = {}) {
  const response = await apiClient.get("/tickets/manager/", { params });
  return response.data.data;
}

export async function getTicketById(id) {
  const response = await apiClient.get(`/tickets/${id}/`);
  return response.data.data;
}

export async function updateTicketStatus(id, status) {
  const response = await apiClient.patch(`/tickets/${id}/status/`, { status });
  return response.data.data;
}
