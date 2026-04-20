import { appConfig } from '@/utils/config'

export interface RequestOptions {
  url: string
  method?: 'GET' | 'POST'
  data?: string | Record<string, any> | ArrayBuffer
  useAiBase?: boolean
  header?: Record<string, string>
}

export function request<T>(options: RequestOptions): Promise<T> {
  const baseUrl = options.useAiBase ? appConfig.aiApiBaseUrl : appConfig.apiBaseUrl
  const token = uni.getStorageSync('silver-shield-mobile-auth-token')

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${baseUrl}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      timeout: appConfig.apiTimeout,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.header || {}),
      },
      success: (response) => resolve(response.data as T),
      fail: reject,
    })
  })
}
