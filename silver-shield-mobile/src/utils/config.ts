export const appConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'https://api.example.com',
  aiApiBaseUrl: import.meta.env.VITE_AI_API_BASE_URL || 'https://ai-api.example.com',
  appEnv: import.meta.env.VITE_APP_ENV || 'development',
  apiTimeout: Number(import.meta.env.VITE_API_TIMEOUT || 10000),
}
