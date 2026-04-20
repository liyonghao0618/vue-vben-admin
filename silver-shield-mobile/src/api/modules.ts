export const backendModules = {
  main: {
    login: '/api/mobile/auth/login',
    profile: '/api/mobile/users/me',
    binding: '/api/mobile/relations',
    alerts: '/api/mobile/alerts',
    sos: '/api/mobile/sos'
  },
  ai: {
    messageDetect: '/api/fraud-detect',
    chatLogDetect: '/api/fraud-detect/chat-log',
    linkDetect: '/api/fraud-detect/link'
  }
}
