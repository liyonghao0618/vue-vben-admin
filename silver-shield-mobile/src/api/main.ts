import { request } from '@/api/http'
import { backendModules } from '@/api/modules'
import { appConfig } from '@/utils/config'
import type {
  Contact,
  ElderProfile,
  LoginForm,
  RiskRecord,
  UserProfile,
  UserRole,
} from '@/types/app'

export interface AuthLoginResponse {
  token: string
  user: UserProfile
}

export interface BindingResponse {
  contacts: Contact[]
  elders: ElderProfile[]
}

export interface AlertListResponse {
  records: RiskRecord[]
}

interface RequestWithFallbackResult<T> {
  data: T
  fallback: boolean
}

function mockProfileByRole(role: UserRole): UserProfile {
  if (role === 'elder') {
    return {
      id: 'elder-001',
      name: '王阿姨',
      role,
      phone: '138****1024',
      welcomeText: '今天也由我来守护您，遇到可疑消息先别着急。',
    }
  }

  return {
    id: 'guardian-001',
    name: '李女士',
    role,
    phone: '139****7718',
    welcomeText: '今天有 1 条高风险提醒待查看，另有 1 条求助需要优先回访。',
  }
}

function mockBindings(): BindingResponse {
  return {
    contacts: [
      {
        id: 'guardian-li',
        name: '李女士',
        relation: '女儿 / 守护人',
        avatarText: '李',
        isGuardian: true,
        tag: '优先联系',
        note: '收到风险提醒后会优先回拨。',
      },
      {
        id: 'elder-001',
        name: '王阿姨',
        relation: '母亲',
        avatarText: '王',
        tag: '高风险关注',
        note: '今天上午出现“养老金补缴”诈骗话术，需要回访确认。',
      },
      {
        id: 'elder-002',
        name: '赵叔叔',
        relation: '父亲',
        avatarText: '赵',
        tag: '今日已提醒',
        note: '下午已发送按时吃药提醒，晚间建议再联系一次。',
      },
      {
        id: 'neighbour-chen',
        name: '陈叔叔',
        relation: '邻居',
        avatarText: '陈',
        tag: '熟人',
        note: '经常帮忙买菜。',
      },
      {
        id: 'community-zhang',
        name: '张社工',
        relation: '社区网格员',
        avatarText: '张',
        tag: '社区',
        note: '紧急情况可协助上门核实。',
      },
    ],
    elders: [
      {
        id: 'elder-001',
        name: '王阿姨',
        age: 68,
        relation: '母亲',
        statusSummary: '今天上午触发 1 条高风险提醒，暂未再次点击陌生链接。',
        lastContactAt: '今天 09:26',
        lastRiskAt: '今天 09:21',
        riskLevel: 'high',
        riskCountToday: 1,
        pendingAlerts: 1,
        hasActiveSos: true,
        medicationNote: '晚饭后降压药待确认是否已服用。',
      },
      {
        id: 'elder-002',
        name: '赵叔叔',
        age: 71,
        relation: '父亲',
        statusSummary: '状态稳定，下午收到一次服药提醒并已回复。',
        lastContactAt: '今天 15:10',
        riskLevel: 'low',
        riskCountToday: 0,
        pendingAlerts: 0,
        medicationNote: '20:00 前提醒测量血压。',
      },
    ],
  }
}

function mockAlerts(): AlertListResponse {
  return {
    records: [
      {
        id: 'risk-1',
        level: 'high',
        title: '老人端实时风险提醒',
        summary: '聊天中出现“转账到安全账户”和“验证码核验”等高危话术。',
        reason: '命中转账、验证码等强风险词，并带有强操作诱导。',
        suggestion: '立即联系老人停止操作，并回访确认是否已泄露验证码。',
        time: '今天 09:21',
        source: 'chat',
        matchedText: ['转账', '验证码', '安全账户'],
        confidence: 0.91,
        traceKey: 'message-msg-risk-seed',
        detectionStatus: 'fallback',
      },
    ],
  }
}

async function requestWithFallback<T>(
  run: () => Promise<T>,
  fallback: () => T,
): Promise<RequestWithFallbackResult<T>> {
  try {
    if (appConfig.appEnv === 'demo') {
      return {
        data: fallback(),
        fallback: true,
      }
    }

    return {
      data: await run(),
      fallback: false,
    }
  } catch {
    return {
      data: fallback(),
      fallback: true,
    }
  }
}

export function loginByPassword(form: LoginForm): Promise<RequestWithFallbackResult<AuthLoginResponse>> {
  return requestWithFallback(
    () =>
      request<AuthLoginResponse>({
        url: backendModules.main.login,
        method: 'POST',
        data: form,
      }),
    () => ({
      token: `mock-token-${form.role}`,
      user: mockProfileByRole(form.role),
    }),
  )
}

export function fetchUserProfile(role: UserRole): Promise<RequestWithFallbackResult<UserProfile>> {
  return requestWithFallback(
    () =>
      request<UserProfile>({
        url: backendModules.main.profile,
      }),
    () => mockProfileByRole(role),
  )
}

export function fetchBindingRelations(): Promise<RequestWithFallbackResult<BindingResponse>> {
  return requestWithFallback(
    () =>
      request<BindingResponse>({
        url: backendModules.main.binding,
      }),
    mockBindings,
  )
}

export function fetchRiskAlerts(): Promise<RequestWithFallbackResult<AlertListResponse>> {
  return requestWithFallback(
    () =>
      request<AlertListResponse>({
        url: backendModules.main.alerts,
      }),
    mockAlerts,
  )
}
