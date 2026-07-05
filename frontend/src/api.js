// API Base Configuration
// In production, configure VITE_API_URL to point to your hosted FastAPI backend.
// In local development, leave it undefined so requests route through the Vite proxy.
export const API_BASE = import.meta.env.VITE_API_URL || '';
