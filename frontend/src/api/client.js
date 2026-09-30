// Central Axios instance so we configure base URL + auth headers once.
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // e.g. http://127.0.0.1:8000/api
});

// Request interceptor: attach the JWT access token to every outgoing request.
// Runs before each request; reads the token fresh from localStorage so it
// always uses the latest one after login/refresh.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: if the server returns 401 (token expired/invalid),
// clear storage and send the user to /login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      // Avoid infinite redirect loops by checking current path.
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;