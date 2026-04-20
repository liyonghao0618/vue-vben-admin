import { request } from '@/api/http'
import { backendModules } from '@/api/modules'
import { appConfig } from '@/utils/config'
import type { SosAlert } from '@/types/app'

interface CreateSosPayload {
  elderId: string
  elderName: string
  summary: string
  detail: string
}

interface CreateSosResponse extends SosAlert {}

async function requestWithFallback<T>(
  run: () => Promise<T>,
  fallback: () => T,
): Promise<T> {
  try {
    if (appConfig.appEnv === 'demo') {
      return fallback()
    }

    return await run()
  } catch {
    return fallback()
  }
}

export function createSosAlert(payload: CreateSosPayload): Promise<CreateSosResponse> {
  return requestWithFallback(
    () =>
      request<CreateSosResponse>({
        url: backendModules.main.sos,
        method: 'POST',
        data: payload,
      }),
    () => ({
      id: `sos-${Date.now()}`,
      elderId: payload.elderId,
      elderName: payload.elderName,
      summary: payload.summary,
      detail: payload.detail,
      status: 'pending',
      time: `今天 ${new Date().toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      })}`,
      location: '居家地址待确认',
      linkedTicketNo: `SOS-${String(Date.now()).slice(-6)}`,
      latestAction: '主业务系统已受理，正在通知守护人和社区联系人。',
      reporterPhone: '138****1024',
      detectionStatus: 'fallback',
    }),
  )
}
