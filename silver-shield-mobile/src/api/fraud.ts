import { request } from '@/api/http'
import { backendModules } from '@/api/modules'
import { appConfig } from '@/utils/config'
import type { RiskLevel } from '@/types/app'

export interface FraudDetectResult {
  suspicious: boolean
  riskLevel: RiskLevel
  reason: string
  suggestion: string
  matchedText: string[]
  confidence: number
  fallback?: boolean
}

interface MessageDetectPayload {
  text: string
  contactId: string
}

interface ChatLogDetectPayload {
  contactId: string
  messages: Array<{
    id: string
    sender: string
    content: string
    time: string
    type: string
  }>
}

interface LinkDetectPayload {
  url: string
  title?: string
}

function levelFromScore(score: number): RiskLevel {
  if (score >= 0.8) {
    return 'high'
  }

  if (score >= 0.45) {
    return 'medium'
  }

  return 'low'
}

function mockAnalyzeText(text: string): FraudDetectResult {
  const matchedText = ['转账', '验证码', '补贴', '银行卡', '汇款', '点击链接', '短链']
    .filter((keyword) => text.includes(keyword))

  if (matchedText.length === 0) {
    return {
      suspicious: false,
      riskLevel: 'low',
      reason: '当前文本未命中高风险诈骗关键词。',
      suggestion: '继续保持谨慎，涉及金钱、身份信息时先联系家属确认。',
      matchedText: [],
      confidence: 0.18,
    }
  }

  const confidence = Math.min(0.35 + matchedText.length * 0.18, 0.96)
  const riskLevel = levelFromScore(confidence)

  return {
    suspicious: riskLevel !== 'low',
    riskLevel,
    reason: `命中风险词：${matchedText.join('、')}，且语义上包含资金或身份验证诱导。`,
    suggestion: riskLevel === 'high'
      ? '立即停止转账、停止点击链接，并联系守护人核验。'
      : '先不要继续操作，建议把消息转给守护人复核。',
    matchedText,
    confidence,
  }
}

function mockAnalyzeChatLog(
  messages: ChatLogDetectPayload['messages'],
): FraudDetectResult {
  const joined = messages.map((item) => item.content).join('\n')
  const result = mockAnalyzeText(joined)

  if (!result.suspicious && messages.length >= 3) {
    return {
      suspicious: true,
      riskLevel: 'medium',
      reason: '聊天记录中出现连续劝导和操作指令，建议人工复核。',
      suggestion: '请守护人继续回访，确认老人是否仍在与陌生人互动。',
      matchedText: ['连续操作引导'],
      confidence: 0.52,
    }
  }

  return result
}

function mockAnalyzeLink(url: string, title?: string): FraudDetectResult {
  const text = `${title || ''} ${url}`.toLowerCase()
  const matchedText = ['short', 'bonus', 'reward', 'verify', 'promo']
    .filter((keyword) => text.includes(keyword))

  if (!matchedText.length) {
    return {
      suspicious: false,
      riskLevel: 'low',
      reason: '链接来源暂未命中明显风险特征。',
      suggestion: '仍建议由守护人先核验再打开。',
      matchedText: [],
      confidence: 0.2,
    }
  }

  return {
    suspicious: true,
    riskLevel: 'medium',
    reason: `链接中存在可疑标记：${matchedText.join('、')}。`,
    suggestion: '不要在老人端直接打开，建议由守护人先检查链接来源。',
    matchedText,
    confidence: 0.66,
  }
}

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

export function detectFraudMessage(payload: MessageDetectPayload): Promise<FraudDetectResult> {
  return requestWithFallback(
    () =>
      request<FraudDetectResult>({
        url: backendModules.ai.messageDetect,
        method: 'POST',
        data: payload,
        useAiBase: true,
      }),
    () => mockAnalyzeText(payload.text),
  )
}

export function detectFraudChatLog(payload: ChatLogDetectPayload): Promise<FraudDetectResult> {
  return requestWithFallback(
    () =>
      request<FraudDetectResult>({
        url: backendModules.ai.chatLogDetect,
        method: 'POST',
        data: payload,
        useAiBase: true,
      }),
    () => mockAnalyzeChatLog(payload.messages),
  )
}

export function detectFraudLink(payload: LinkDetectPayload): Promise<FraudDetectResult> {
  return requestWithFallback(
    () =>
      request<FraudDetectResult>({
        url: backendModules.ai.linkDetect,
        method: 'POST',
        data: payload,
        useAiBase: true,
      }),
    () => mockAnalyzeLink(payload.url, payload.title),
  )
}

export function createFallbackDetectResult(scope: 'text' | 'chat' | 'link'): FraudDetectResult {
  const labelMap = {
    text: '文本识别',
    chat: '聊天记录识别',
    link: '链接识别',
  }

  return {
    suspicious: false,
    riskLevel: 'low',
    reason: `${labelMap[scope]}服务暂时不可用。`,
    suggestion: '请先保持谨慎，涉及转账、验证码、陌生链接时一律暂停并联系守护人。',
    matchedText: [],
    confidence: 0,
    fallback: true,
  }
}
