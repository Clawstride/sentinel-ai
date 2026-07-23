import axios from "axios";

// Single source of truth for the backend base URL. Configure via
// VITE_API_BASE_URL in an .env file at the frontend project root.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 15000,
});

// Normalizes axios errors into a small, predictable shape so every
// page can handle failures the same way without touching axios internals.
function toApiError(error) {
  if (error.response) {
    const detail = error.response.data?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : detail?.message || error.response.statusText || "Request failed.";
    return { message, status: error.response.status, detail };
  }
  if (error.request) {
    return {
      message:
        "Could not reach the SentinelAI backend. Confirm it is running and reachable.",
      status: null,
    };
  }
  return { message: error.message || "Unexpected error.", status: null };
}

async function request(promise) {
  try {
    const response = await promise;
    return response.data;
  } catch (error) {
    throw toApiError(error);
  }
}

// ---- Logs ---------------------------------------------------------------

export function uploadLogFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request(
    client.post("/logs/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
  );
}

// ---- Incidents ------------------------------------------------------------

export function generateIncidents() {
  return request(client.post("/incidents/generate"));
}

export function listIncidents() {
  return request(client.get("/incidents"));
}

export function getIncident(incidentId) {
  return request(client.get(`/incidents/${incidentId}`));
}

export function getIncidentInvestigation(incidentId) {
  return request(client.get(`/incidents/${incidentId}/investigation`));
}

export function updateIncidentStatus(incidentId, status) {
  return request(client.patch(`/incidents/${incidentId}/status`, { status }));
}

export function updateIncidentNotes(incidentId, notes) {
  return request(client.patch(`/incidents/${incidentId}/notes`, { notes }));
}

// ---- Dashboard ------------------------------------------------------------

export function getDashboardSummary() {
  return request(client.get("/dashboard/summary"));
}

export { BASE_URL };
