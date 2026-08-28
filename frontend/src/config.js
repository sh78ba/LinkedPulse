// Centralized API Base URL configuration
// In development, Vite proxies requests from '' to http://localhost:8000
// When hosted, set your deployed backend URL here or via the VITE_API_URL environment variable

export const API_BASE_URL =
  import.meta.env.VITE_API_URL || ''; 
  // Example for hardcoding:
  // export const API_BASE_URL = 'https://your-backend-service.onrender.com';
