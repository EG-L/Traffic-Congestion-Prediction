import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 10000,
  headers: {
    "X-Token": import.meta.env.VITE_API_TOKEN || "",
  },
});

export const trafficAPI = {
  getRealtime: () => api.get("/api/traffic/realtime"),
  getRoad: (roadId) => api.get(`/api/traffic/realtime/${roadId}`),
};

export const weatherAPI = {
  getCurrent: () => api.get("/api/weather/current"),
};

export const predictionAPI = {
  getAll: () => api.get("/api/prediction/all"),
  getRoad: (roadId) => api.get(`/api/prediction/${roadId}`),
};

export const cctvAPI = {
  getNearby: (lat, lng, radius = 0.15) =>
    api.get("/api/cctv/nearby", { params: { lat, lng, radius } }),
};
