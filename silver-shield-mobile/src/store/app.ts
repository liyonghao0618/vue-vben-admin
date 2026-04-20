import { defineStore } from 'pinia'
import {
  fetchBindingRelations,
  fetchRiskAlerts,
  fetchUserProfile,
  loginByPassword,
} from '@/api/main'
import {
  createFallbackDetectResult,
  detectFraudChatLog,
  detectFraudLink,
  detectFraudMessage,
} from '@/api/fraud'
import { createSosAlert } from '@/api/sos'
import type {
  ChatSession,
  ChatMessage,
  Contact,
  ElderProfile,
  ElderSettings,
  LoginForm,
  RemoteReminder,
  RiskRecord,
  SosAlert,
  UserProfile,
  UserRole,
  ActiveCallSession,
  CallRecord,
  CallStatus,
  NetworkStatus,
  RiskTrendPoint,
} from '@/types/app'

const STORAGE_KEY = 'silver-shield-mobile-app-state'
const AUTH_TOKEN_KEY = 'silver-shield-mobile-auth-token'

interface PersistedState {
  isLoggedIn: boolean
  currentRole: UserRole
  selectedContactId: string
  selectedElderId: string
  selectedRiskId: string
  selectedSosId: string
  elderSettings: ElderSettings
  profile: UserProfile | null
  selectedCallRecordId: string
}

interface AppState extends PersistedState {
  authToken: string
  contacts: Contact[]
  elders: ElderProfile[]
  messages: ChatMessage[]
  riskRecords: RiskRecord[]
  remoteReminders: RemoteReminder[]
  sosAlerts: SosAlert[]
  sosCount: number
  loginError: string
  aiServiceNotice: string
  mainServiceNotice: string
  analyzedConversationIds: string[]
  analyzedLinkTraceKeys: string[]
  activeCallSession: ActiveCallSession | null
  callRecords: CallRecord[]
  selectedCallRecordId: string
  callSdkPlan: string
  networkType: string
  networkStatus: NetworkStatus
  lastRiskRefreshAt: string
}

const defaultPersistedState: PersistedState = {
  isLoggedIn: false,
  currentRole: 'elder',
  selectedContactId: 'guardian-li',
  selectedElderId: 'elder-001',
  selectedRiskId: 'risk-1',
  selectedSosId: 'sos-1',
  elderSettings: {
    fontScale: 'x-large',
    contrastMode: true,
    voiceBroadcastReserved: true,
    simplifyMode: true,
  },
  profile: null,
  selectedCallRecordId: 'call-record-1',
}

function getPersistedState(): Partial<PersistedState> {
  try {
    const raw = uni.getStorageSync(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as Partial<PersistedState>) : {}
  } catch (error) {
    console.warn('failed to restore storage', error)
    return {}
  }
}

function persistState(payload: PersistedState) {
  uni.setStorageSync(STORAGE_KEY, JSON.stringify(payload))
}

function formatCurrentTime() {
  return new Date().toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

function formatDisplayTime() {
  return `今天 ${formatCurrentTime()}`
}

function formatDuration(seconds: number) {
  const mins = Math.floor(seconds / 60)
  const remain = seconds % 60

  return `${String(mins).padStart(2, '0')}:${String(remain).padStart(2, '0')}`
}

function buildRiskTrendPoints(records: RiskRecord[]): RiskTrendPoint[] {
  const labels = ['近三天', '前天', '昨天', '今天']

  return labels.map((label, index) => {
    const offset = labels.length - index
    const high = records.filter((item) => item.level === 'high').length
    const medium = records.filter((item) => item.level === 'medium').length
    const low = records.filter((item) => item.level === 'low').length

    return {
      label,
      high: Math.max(high - offset + 1, 0),
      medium: Math.max(medium - Math.floor(offset / 2), 0),
      low: low + index,
    }
  })
}

function buildCallSummaryRisk(summaryText: string): {
  level: RiskRecord['level']
  action: string
} {
  const content = summaryText.toLowerCase()

  if (content.includes('诈骗') || content.includes('转账') || content.includes('验证码')) {
    return {
      level: 'high',
      action: '建议继续电话回访，并同步拉黑号码和社区协查。',
    }
  }

  if (content.includes('回拨') || content.includes('核验') || content.includes('未接通')) {
    return {
      level: 'medium',
      action: '建议安排再次回拨，并保留本次记录给守护人查看。',
    }
  }

  return {
    level: 'low',
    action: '本次通话风险较低，建议继续日常关怀即可。',
  }
}

function buildAutoReply(contactId: string, content: string): ChatMessage | null {
  const time = formatCurrentTime()

  if (contactId === 'guardian-li') {
    return {
      id: `reply-${Date.now()}`,
      contactId,
      sender: 'other',
      type: 'text',
      content: content.includes('链接')
        ? '先别点，我帮你看一下来源。'
        : '收到，遇到不确定的事情先发给我就对了。',
      time,
      status: 'received',
    }
  }

  if (contactId.startsWith('elder-')) {
    return {
      id: `reply-${Date.now()}`,
      contactId,
      sender: 'other',
      type: 'text',
      content: content.includes('别转账')
        ? '好的，我先不操作，等你确认。'
        : '我看到了，先按你说的做。',
      time,
      status: 'received',
    }
  }

  return null
}

function buildRiskTitle(contactId: string, level: RiskRecord['level']) {
  if (contactId === 'guardian-li') {
    return level === 'high' ? '老人端实时风险提醒' : '老人端可疑消息提醒'
  }

  if (contactId === 'elder-001') {
    return '王阿姨聊天风险提醒'
  }

  if (contactId === 'elder-002') {
    return '赵叔叔聊天风险提醒'
  }

  return '聊天风险提醒'
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    ...defaultPersistedState,
    ...getPersistedState(),
    authToken: '',
    contacts: [
      {
        id: 'guardian-li',
        name: '李女士',
        relation: '女儿 / 守护人',
        avatarText: '李',
        isGuardian: true,
        tag: '优先联系',
        note: '收到风险提醒后会优先回拨。',
        isPriority: true,
        suspiciousLevel: 'none',
      },
      {
        id: 'elder-001',
        name: '王阿姨',
        relation: '母亲',
        avatarText: '王',
        tag: '高风险关注',
        note: '今天上午出现“养老金补缴”诈骗话术，需要回访确认。',
        isPriority: true,
        suspiciousLevel: 'high',
        isBlacklisted: false,
        supportsCommunityAssist: true,
      },
      {
        id: 'elder-002',
        name: '赵叔叔',
        relation: '父亲',
        avatarText: '赵',
        tag: '今日已提醒',
        note: '下午已发送按时吃药提醒，晚间建议再联系一次。',
        isPriority: true,
        suspiciousLevel: 'low',
        isBlacklisted: false,
        supportsCommunityAssist: true,
      },
      {
        id: 'neighbour-chen',
        name: '陈叔叔',
        relation: '邻居',
        avatarText: '陈',
        tag: '熟人',
        note: '经常帮忙买菜。',
        suspiciousLevel: 'none',
      },
      {
        id: 'community-zhang',
        name: '张社工',
        relation: '社区网格员',
        avatarText: '张',
        tag: '社区',
        note: '紧急情况可协助上门核实。',
        isPriority: true,
        suspiciousLevel: 'none',
        supportsCommunityAssist: true,
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
    messages: [
      {
        id: 'msg-1',
        contactId: 'guardian-li',
        sender: 'other',
        type: 'text',
        content: '妈，今天如果有人让你转账，先发消息给我。',
        time: '09:18',
        status: 'received',
      },
      {
        id: 'msg-2',
        contactId: 'guardian-li',
        sender: 'self',
        type: 'text',
        content: '好，我先问你再处理。',
        time: '09:20',
        status: 'sent',
      },
      {
        id: 'msg-3',
        contactId: 'guardian-li',
        sender: 'system',
        type: 'text',
        content: '检测到“补贴补缴”相关高风险话术，建议暂停转账。',
        time: '09:21',
        status: 'risk',
        riskLevel: 'high',
        suspicious: true,
        riskReason: '命中高风险资金诱导词。',
      },
      {
        id: 'msg-3a',
        contactId: 'guardian-li',
        sender: 'other',
        type: 'link',
        content: '这个链接看着很奇怪，我没点开。',
        time: '09:22',
        status: 'received',
        linkUrl: 'https://safe-check.example/link-preview',
        linkTitle: '陌生补贴链接待核验',
      },
      {
        id: 'msg-4',
        contactId: 'elder-001',
        sender: 'other',
        type: 'text',
        content: '女儿，刚才有人说可以代办养老金补缴，我先没转。',
        time: '09:23',
        status: 'received',
      },
      {
        id: 'msg-5',
        contactId: 'elder-001',
        sender: 'self',
        type: 'text',
        content: '先不要点链接，也不要转账，我马上给你打字确认。',
        time: '09:24',
        status: 'sent',
      },
      {
        id: 'msg-6',
        contactId: 'elder-001',
        sender: 'system',
        type: 'text',
        content: '系统同步：已向守护人推送高风险提醒，并生成回访建议。',
        time: '09:25',
        status: 'risk',
        riskLevel: 'high',
        suspicious: true,
        riskReason: '聊天记录已被识别为高风险。',
      },
      {
        id: 'msg-6a',
        contactId: 'elder-001',
        sender: 'other',
        type: 'image',
        content: '图片消息预留：可疑聊天截图',
        time: '09:26',
        status: 'received',
        previewImageUrl: '/static/chat-image-placeholder.png',
        ocrStatus: 'done',
        ocrText: '图片识别预留结果：补缴通知、验证码、官方客服。',
      },
      {
        id: 'msg-7',
        contactId: 'elder-002',
        sender: 'self',
        type: 'text',
        content: '爸，晚上记得先量血压再吃药。',
        time: '15:00',
        status: 'sent',
      },
      {
        id: 'msg-8',
        contactId: 'elder-002',
        sender: 'other',
        type: 'text',
        content: '好的，我吃完饭就量。',
        time: '15:10',
        status: 'received',
      },
    ],
    riskRecords: [
      {
        id: 'risk-1',
        level: 'high',
        title: '王阿姨转账劝阻提醒',
        summary: '系统识别到“代办养老金补缴”话术，建议暂停转账并立即回访老人。',
        reason: '消息中出现补缴养老金、紧急转账、代办资格等组合词。',
        suggestion: '先通过聊天确认老人当前是否还在与对方联系，再电话回访并协助拉黑号码。',
        time: '今天 09:21',
        source: 'chat',
        matchedText: ['补缴养老金', '紧急转账', '代办资格'],
        confidence: 0.92,
        traceKey: 'seed-risk-1',
        detectionStatus: 'success',
        relatedContactId: 'elder-001',
        followUpStatus: 'processing',
      },
      {
        id: 'risk-2',
        level: 'medium',
        title: '陌生链接预警',
        summary: '检测到短链跳转，建议由守护人先核验来源。',
        reason: '链接域名与历史常用联系人来源不一致。',
        suggestion: '请家属代为打开查看，老人端不直接点击。',
        time: '昨天 19:45',
        source: 'link',
        matchedText: ['短链跳转'],
        confidence: 0.66,
        traceKey: 'seed-risk-2',
        detectionStatus: 'success',
        relatedContactId: 'guardian-li',
        followUpStatus: 'pending',
      },
      {
        id: 'risk-3',
        level: 'medium',
        title: '通话后复盘提醒',
        summary: '上一次回访通话中提到“继续帮我核验链接”，建议继续跟进链接来源。',
        reason: '通话摘要中提到陌生链接和回拨核验，建议补充聊天确认。',
        suggestion: '继续追问链接来源，并视情况同步社区协助核验。',
        time: '今天 09:35',
        source: 'call',
        matchedText: ['陌生链接', '回拨核验'],
        confidence: 0.58,
        traceKey: 'seed-risk-3',
        detectionStatus: 'success',
        relatedContactId: 'elder-001',
        followUpStatus: 'pending',
      },
    ],
    remoteReminders: [
      {
        id: 'remind-1',
        elderId: 'elder-002',
        content: '晚饭后记得先量血压，再吃药。',
        channel: 'care',
        time: '今天 15:00',
      },
    ],
    sosAlerts: [
      {
        id: 'sos-1',
        elderId: 'elder-001',
        elderName: '王阿姨',
        summary: '老人触发了一键求助，希望你尽快联系并确认是否需要社区协助。',
        status: 'pending',
        time: '今天 09:28',
        detail: '老人表示接到可疑来电后情绪紧张，希望家属尽快联系。',
        location: '浦东新区居家地址',
        linkedTicketNo: 'SOS-240928',
        latestAction: '主业务系统已通知李女士与社区网格员。',
        reporterPhone: '138****1024',
        detectionStatus: 'success',
      },
    ],
    sosCount: 0,
    loginError: '',
    aiServiceNotice: '',
    mainServiceNotice: '',
    analyzedConversationIds: [],
    analyzedLinkTraceKeys: [],
    activeCallSession: null,
    callRecords: [
      {
        id: 'call-record-1',
        contactId: 'guardian-li',
        contactName: '李女士',
        roleView: 'elder',
        direction: 'outgoing',
        status: 'ended',
        startedAt: '今天 09:27',
        endedAt: '今天 09:31',
        durationSeconds: 248,
        durationLabel: formatDuration(248),
        summaryStatus: 'uploaded',
        summaryText: '已确认对方是诈骗话术，老人未转账，家属将继续回访。',
        sdkPlan: '预留接入 App 内 RTC SDK 的会后摘要上传能力。',
        postCallRiskLevel: 'high',
        followUpAction: '建议继续拉黑号码并同步社区关注。',
      },
      {
        id: 'call-record-2',
        contactId: 'elder-001',
        contactName: '王阿姨',
        roleView: 'guardian',
        direction: 'outgoing',
        status: 'missed',
        startedAt: '今天 09:29',
        endedAt: '今天 09:29',
        durationSeconds: 0,
        durationLabel: formatDuration(0),
        summaryStatus: 'pending',
        summaryText: '未接通，建议继续回拨并同步社区协助。',
        sdkPlan: '预留接入 App 内 RTC SDK 的会后摘要上传能力。',
        postCallRiskLevel: 'medium',
        followUpAction: '建议稍后再次回拨，并保留社区协助入口。',
      },
    ],
    selectedCallRecordId: 'call-record-1',
    callSdkPlan: '当前为本地演示状态机，后续可替换为 Agora / ZEGO / Tencent RTC 等 App 内语音方案。',
    networkType: 'unknown',
    networkStatus: 'unknown',
    lastRiskRefreshAt: '',
  }),
  getters: {
    elderName: (state) => (state.profile?.role === 'elder' ? state.profile.name : '王阿姨'),
    guardianName: (state) => (state.profile?.role === 'guardian' ? state.profile.name : '李女士'),
    selectedContact(state): Contact | undefined {
      return state.contacts.find((item) => item.id === state.selectedContactId)
    },
    selectedMessages(state): ChatMessage[] {
      return state.messages.filter((item) => item.contactId === state.selectedContactId)
    },
    latestHighRisk(state): RiskRecord | undefined {
      return state.riskRecords.find((item) => item.level === 'high')
    },
    selectedElder(state): ElderProfile | undefined {
      return state.elders.find((item) => item.id === state.selectedElderId)
    },
    guardianElders(state): ElderProfile[] {
      return state.elders
    },
    guardianRiskRecords(state): RiskRecord[] {
      return state.riskRecords
    },
    riskTrendPoints(state): RiskTrendPoint[] {
      return buildRiskTrendPoints(state.riskRecords)
    },
    priorityContacts(state): Contact[] {
      return state.contacts.filter((item) => item.isPriority)
    },
    suspiciousContacts(state): Contact[] {
      return state.contacts.filter((item) => item.suspiciousLevel && item.suspiciousLevel !== 'none')
    },
    blacklistedContacts(state): Contact[] {
      return state.contacts.filter((item) => item.isBlacklisted)
    },
    communityContacts(state): Contact[] {
      return state.contacts.filter((item) => item.supportsCommunityAssist)
    },
    selectedRisk(state): RiskRecord | undefined {
      return state.riskRecords.find((item) => item.id === state.selectedRiskId)
    },
    selectedSosAlert(state): SosAlert | undefined {
      return state.sosAlerts.find((item) => item.id === state.selectedSosId)
    },
    pendingHighRiskCount(state): number {
      return state.riskRecords.filter((item) => item.level === 'high').length
    },
    activeSosAlerts(state): SosAlert[] {
      return state.sosAlerts.filter((item) => item.status !== 'resolved')
    },
    selectedCallRecord(state): CallRecord | undefined {
      return state.callRecords.find((item) => item.id === state.selectedCallRecordId)
    },
    elderCallRecords(state): CallRecord[] {
      return state.callRecords.filter((item) => item.roleView === 'elder')
    },
    guardianCallRecords(state): CallRecord[] {
      return state.callRecords.filter((item) => item.roleView === 'guardian')
    },
    isWeakNetwork(state): boolean {
      return state.networkStatus === 'weak' || state.networkStatus === 'offline'
    },
    chatSessions(state): ChatSession[] {
      return state.contacts
        .filter((contact) => state.messages.some((message) => message.contactId === contact.id))
        .map((contact) => {
          const relatedMessages = state.messages
            .filter((message) => message.contactId === contact.id)
            .sort((a, b) => a.time.localeCompare(b.time))
          const latestMessage = relatedMessages[relatedMessages.length - 1]
          const unreadCount = relatedMessages.filter(
            (message) => message.sender === 'other' && message.status === 'received',
          ).length

          return {
            contactId: contact.id,
            name: contact.name,
            relation: contact.relation,
            avatarText: contact.avatarText,
            tag: contact.tag,
            lastMessage: latestMessage?.content || '暂无消息',
            lastMessageTime: latestMessage?.time || '--:--',
            lastMessageStatus: latestMessage?.status || 'sent',
            unreadCount,
            hasRisk: relatedMessages.some((message) => message.status === 'risk' || message.suspicious),
            messageType: latestMessage?.type || 'text',
          }
        })
        .sort((a, b) => b.lastMessageTime.localeCompare(a.lastMessageTime))
    },
  },
  actions: {
    savePersistedState() {
      persistState({
        isLoggedIn: this.isLoggedIn,
        currentRole: this.currentRole,
        selectedContactId: this.selectedContactId,
        selectedElderId: this.selectedElderId,
        selectedRiskId: this.selectedRiskId,
        selectedSosId: this.selectedSosId,
        elderSettings: this.elderSettings,
        profile: this.profile,
        selectedCallRecordId: this.selectedCallRecordId,
      })
    },
    setRole(role: UserRole) {
      this.currentRole = role
      this.savePersistedState()
    },
    async login(form: LoginForm) {
      this.loginError = ''
      this.mainServiceNotice = ''

      if (!form.account || !form.password) {
        this.loginError = '请输入账号和密码'
        return false
      }

      try {
        const { data, fallback } = await loginByPassword(form)

        this.currentRole = data.user.role || form.role
        this.profile = data.user
        this.authToken = data.token
        this.isLoggedIn = true
        uni.setStorageSync(AUTH_TOKEN_KEY, data.token)

        if (fallback) {
          this.mainServiceNotice = '登录接口当前使用演示回执，后续可直接切换到真实主业务系统。'
        }

        await Promise.all([
          this.loadUserProfile(),
          this.loadBindingRelations(),
          this.loadRiskAlerts(),
        ])
        this.savePersistedState()
        return true
      } catch {
        this.loginError = '登录失败，请稍后重试'
        return false
      }
    },
    logout() {
      this.isLoggedIn = false
      this.authToken = ''
      this.profile = null
      this.currentRole = 'elder'
      this.selectedContactId = 'guardian-li'
      this.selectedElderId = 'elder-001'
      this.selectedRiskId = 'risk-1'
      this.selectedSosId = 'sos-1'
      this.selectedCallRecordId = 'call-record-1'
      this.aiServiceNotice = ''
      this.mainServiceNotice = ''
      this.activeCallSession = null
      uni.removeStorageSync(AUTH_TOKEN_KEY)
      this.savePersistedState()
    },
    async loadUserProfile() {
      const { data, fallback } = await fetchUserProfile(this.currentRole)
      this.profile = data

      if (fallback) {
        this.mainServiceNotice = '用户信息当前来自演示数据，联调后会展示真实账户资料。'
      }

      this.savePersistedState()
    },
    async loadBindingRelations() {
      const { data, fallback } = await fetchBindingRelations()
      this.contacts = data.contacts
      this.elders = data.elders

      if (fallback) {
        this.mainServiceNotice = '绑定关系当前使用演示数据，联调后会按真实监护关系展示。'
      }
    },
    async loadRiskAlerts() {
      const { data, fallback } = await fetchRiskAlerts()

      for (const record of data.records) {
        this.upsertRiskRecord(record)
      }

      if (fallback) {
        this.mainServiceNotice = '风险通知当前使用演示数据，联调后会同步主业务系统告警流。'
      }
    },
    selectContact(contactId: string) {
      this.selectedContactId = contactId
      this.savePersistedState()
      void this.analyzeConversation(contactId)
      void this.analyzeLinks(contactId)
    },
    selectElder(elderId: string) {
      this.selectedElderId = elderId
      this.selectedContactId = elderId
      this.savePersistedState()
      void this.analyzeConversation(elderId)
      void this.analyzeLinks(elderId)
    },
    selectRisk(riskId: string) {
      this.selectedRiskId = riskId
      this.savePersistedState()
    },
    selectSosAlert(sosId: string) {
      this.selectedSosId = sosId
      this.savePersistedState()
    },
    selectCallRecord(recordId: string) {
      this.selectedCallRecordId = recordId
      this.savePersistedState()
    },
    setAiServiceNotice(message: string) {
      this.aiServiceNotice = message
    },
    updateNetworkState(networkType: string, isConnected: boolean) {
      this.networkType = networkType

      if (!isConnected || networkType === 'none') {
        this.networkStatus = 'offline'
        return
      }

      if (['2g', '3g', 'unknown'].includes(networkType)) {
        this.networkStatus = 'weak'
        return
      }

      this.networkStatus = 'online'
    },
    initNetworkStatus() {
      uni.getNetworkType({
        success: ({ networkType }) => {
          this.updateNetworkState(networkType, networkType !== 'none')
        },
        fail: () => {
          this.networkType = 'unknown'
          this.networkStatus = 'unknown'
        },
      })

      uni.onNetworkStatusChange(({ isConnected, networkType }) => {
        this.updateNetworkState(networkType, isConnected)
      })
    },
    upsertRiskRecord(record: RiskRecord) {
      const index = this.riskRecords.findIndex((item) => item.traceKey === record.traceKey)
      if (index >= 0) {
        this.riskRecords[index] = {
          ...this.riskRecords[index],
          ...record,
        }
      } else {
        this.riskRecords.unshift(record)
      }

      if (record.id) {
        this.selectedRiskId = record.id
      }
    },
    async analyzeMessage(messageId: string) {
      const target = this.messages.find((item) => item.id === messageId)
      if (!target || target.type !== 'text' || target.sender === 'system') {
        return
      }

      try {
        const result = await detectFraudMessage({
          text: target.content,
          contactId: target.contactId,
        })

        target.suspicious = result.suspicious
        target.riskLevel = result.suspicious ? result.riskLevel : undefined
        target.riskReason = result.reason

        if (result.suspicious) {
          this.messages.push({
            id: `risk-${Date.now()}`,
            contactId: target.contactId,
            sender: 'system',
            type: 'text',
            content: `${result.riskLevel === 'high' ? '高风险' : '风险'}提醒：${result.suggestion}`,
            time: formatCurrentTime(),
            status: 'risk',
            riskLevel: result.riskLevel,
            suspicious: true,
            riskReason: result.reason,
          })

          const riskId = `risk-${messageId}`
          this.upsertRiskRecord({
            id: riskId,
            level: result.riskLevel,
            title: buildRiskTitle(target.contactId, result.riskLevel),
            summary: `消息“${target.content}”触发了${result.riskLevel === 'high' ? '高' : '中'}风险识别。`,
            reason: result.reason,
            suggestion: result.suggestion,
            time: formatDisplayTime(),
            source: 'chat',
            matchedText: result.matchedText,
            confidence: result.confidence,
            traceKey: `message-${messageId}`,
            detectionStatus: result.fallback ? 'fallback' : 'success',
          })
        }

        if (result.fallback) {
          this.aiServiceNotice = createFallbackDetectResult('text').suggestion
        }
      } catch {
        const fallback = createFallbackDetectResult('text')
        this.aiServiceNotice = fallback.suggestion
      }
    },
    async analyzeConversation(contactId: string) {
      if (this.analyzedConversationIds.includes(contactId)) {
        return
      }

      const relatedMessages = this.messages
        .filter((item) => item.contactId === contactId && item.sender !== 'system')
        .slice(-6)

      if (!relatedMessages.length) {
        return
      }

      try {
        const result = await detectFraudChatLog({
          contactId,
          messages: relatedMessages.map((item) => ({
            id: item.id,
            sender: item.sender,
            content: item.content,
            time: item.time,
            type: item.type,
          })),
        })

        this.analyzedConversationIds.push(contactId)

        if (result.suspicious) {
          this.upsertRiskRecord({
            id: `chatlog-${contactId}`,
            level: result.riskLevel,
            title: `${buildRiskTitle(contactId, result.riskLevel)}（聊天记录）`,
            summary: '聊天记录整体命中诈骗风险模式，建议优先回访。',
            reason: result.reason,
            suggestion: result.suggestion,
            time: formatDisplayTime(),
            source: 'chat',
            matchedText: result.matchedText,
            confidence: result.confidence,
            traceKey: `chatlog-${contactId}`,
            detectionStatus: result.fallback ? 'fallback' : 'success',
          })
        }

        if (result.fallback) {
          this.aiServiceNotice = createFallbackDetectResult('chat').suggestion
        }
      } catch {
        const fallback = createFallbackDetectResult('chat')
        this.aiServiceNotice = fallback.suggestion
      }
    },
    async analyzeLinks(contactId: string) {
      const linkMessages = this.messages.filter(
        (item) => item.contactId === contactId && item.type === 'link' && item.linkUrl,
      )

      for (const message of linkMessages) {
        const traceKey = `link-${message.id}`
        if (this.analyzedLinkTraceKeys.includes(traceKey)) {
          continue
        }

        try {
          const result = await detectFraudLink({
            url: message.linkUrl || '',
            title: message.linkTitle,
          })

          this.analyzedLinkTraceKeys.push(traceKey)
          message.suspicious = result.suspicious
          message.riskLevel = result.suspicious ? result.riskLevel : undefined
          message.riskReason = result.reason

          if (result.suspicious) {
            this.upsertRiskRecord({
              id: `linkrisk-${message.id}`,
              level: result.riskLevel,
              title: '陌生链接识别提醒',
              summary: `链接“${message.linkTitle || message.linkUrl}”存在可疑特征。`,
              reason: result.reason,
              suggestion: result.suggestion,
              time: formatDisplayTime(),
              source: 'link',
              matchedText: result.matchedText,
              confidence: result.confidence,
              traceKey,
              detectionStatus: result.fallback ? 'fallback' : 'success',
            })
          }

          if (result.fallback) {
            this.aiServiceNotice = createFallbackDetectResult('link').suggestion
          }
        } catch {
          const fallback = createFallbackDetectResult('link')
          this.aiServiceNotice = fallback.suggestion
        }
      }
    },
    async sendMessage(content: string) {
      const trimmed = content.trim()
      if (!trimmed) {
        return
      }

      const time = formatCurrentTime()
      const messageId = `msg-${Date.now()}`

      this.messages.push({
        id: messageId,
        contactId: this.selectedContactId,
        sender: 'self',
        type: 'text',
        content: trimmed,
        time,
        status: 'sent',
      })

      const reply = buildAutoReply(this.selectedContactId, trimmed)
      if (reply) {
        this.messages.push(reply)
      }

      await this.analyzeMessage(messageId)
      await this.analyzeConversation(this.selectedContactId)
      await this.analyzeLinks(this.selectedContactId)
    },
    async sendImageMessage(payload: { title: string; previewImageUrl?: string; ocrText?: string }) {
      const title = payload.title.trim()
      if (!title) {
        return
      }

      const time = formatCurrentTime()
      const messageId = `img-${Date.now()}`

      this.messages.push({
        id: messageId,
        contactId: this.selectedContactId,
        sender: 'self',
        type: 'image',
        content: `图片消息预留：${title}`,
        time,
        status: 'sent',
        previewImageUrl: payload.previewImageUrl || '/static/chat-image-placeholder.png',
        ocrStatus: payload.ocrText ? 'done' : 'pending',
        ocrText: payload.ocrText,
      })

      if (payload.ocrText) {
        const result = await detectFraudMessage({
          text: payload.ocrText,
          contactId: this.selectedContactId,
        })

        if (result.suspicious) {
          this.upsertRiskRecord({
            id: `ocr-${messageId}`,
            level: result.riskLevel,
            title: '图片 OCR 风险提醒',
            summary: `图片提取文字“${payload.ocrText}”命中风险识别，建议立即人工核验。`,
            reason: result.reason,
            suggestion: result.suggestion,
            time: formatDisplayTime(),
            source: 'chat',
            matchedText: result.matchedText,
            confidence: result.confidence,
            traceKey: `ocr-${messageId}`,
            detectionStatus: result.fallback ? 'fallback' : 'success',
            relatedContactId: this.selectedContactId,
            followUpStatus: 'pending',
          })
        }
      }
    },
    async refreshRiskSignals(contactId?: string) {
      const targetId = contactId || this.selectedContactId
      this.aiServiceNotice = ''
      this.analyzedConversationIds = this.analyzedConversationIds.filter((item) => item !== targetId)
      this.analyzedLinkTraceKeys = this.analyzedLinkTraceKeys.filter((item) => !item.startsWith(`link-`))
      await this.analyzeConversation(targetId)
      await this.analyzeLinks(targetId)
      this.lastRiskRefreshAt = formatDisplayTime()
    },
    async submitSos() {
      const summary = '老人刚刚发起一键求助，请尽快回访并确认是否需要社区上门。'
      const detail = '疑似遇到诈骗来电后主动发起求助，系统建议守护人立即回访并确认当前位置。'

      const sosAlert = await createSosAlert({
        elderId: 'elder-001',
        elderName: '王阿姨',
        summary,
        detail,
      })

      this.sosCount += 1
      this.sosAlerts.unshift(sosAlert)
      this.selectedSosId = sosAlert.id
      this.mainServiceNotice = sosAlert.detectionStatus === 'fallback'
        ? '主业务系统当前使用演示回执，请继续按流程回访老人。'
        : '主业务系统已记录本次求助，并同步通知守护人。'
      this.savePersistedState()
    },
    sendRemoteReminder(content: string) {
      const elder = this.selectedElder
      if (!elder || !content.trim()) {
        return
      }

      const now = formatCurrentTime()
      const reminder: RemoteReminder = {
        id: `remind-${Date.now()}`,
        elderId: elder.id,
        content: content.trim(),
        channel: 'care',
        time: `今天 ${now}`,
      }

      this.remoteReminders.unshift(reminder)
      this.messages.push({
        id: `reminder-msg-${Date.now()}`,
        contactId: elder.id,
        sender: 'self',
        type: 'text',
        content: `远程提醒：${content.trim()}`,
        time: now,
        status: 'sent',
      })
    },
    markSosHandled(alertId: string) {
      this.sosAlerts = this.sosAlerts.map((item) =>
        item.id === alertId
          ? {
            ...item,
            status: 'processing',
            latestAction: '守护人已接单，正在电话回访老人并联系社区确认。',
          }
          : item,
      )
    },
    resolveSosAlert(alertId: string) {
      this.sosAlerts = this.sosAlerts.map((item) =>
        item.id === alertId
          ? {
            ...item,
            status: 'resolved',
            latestAction: '本次求助已完成处置，主业务系统已记录处理结果。',
          }
          : item,
      )
    },
    startCall(contactId: string, roleView: UserRole, direction: 'incoming' | 'outgoing' = 'outgoing') {
      const contact = this.contacts.find((item) => item.id === contactId)
      const elder = this.elders.find((item) => item.id === contactId)
      const name = contact?.name || elder?.name || '未命名联系人'
      const relation = contact?.relation || elder?.relation || '联系人'
      const avatarText = contact?.avatarText || name.slice(0, 1)

      this.activeCallSession = {
        id: `call-${Date.now()}`,
        contactId,
        contactName: name,
        relation,
        avatarText,
        roleView,
        direction,
        status: 'ringing',
        startedAt: formatDisplayTime(),
        durationSeconds: 0,
        sdkPlan: this.callSdkPlan,
        summaryDraft: direction === 'incoming'
          ? '已预留接听后摘要上传字段，可记录本次通话结论。'
          : '已预留拨打后摘要上传字段，可记录是否劝阻成功。',
      }
    },
    acceptCurrentCall() {
      if (!this.activeCallSession) {
        return
      }

      this.activeCallSession = {
        ...this.activeCallSession,
        status: 'connecting',
      }
    },
    connectCurrentCall() {
      if (!this.activeCallSession) {
        return
      }

      this.activeCallSession = {
        ...this.activeCallSession,
        status: 'connected',
        connectedAt: formatDisplayTime(),
      }
    },
    tickCurrentCall(seconds = 1) {
      if (!this.activeCallSession || this.activeCallSession.status !== 'connected') {
        return
      }

      this.activeCallSession = {
        ...this.activeCallSession,
        durationSeconds: this.activeCallSession.durationSeconds + seconds,
      }
    },
    endCurrentCall(status: 'ended' | 'failed' | 'missed' | 'rejected', errorMessage?: string) {
      if (!this.activeCallSession) {
        return
      }

      const session = {
        ...this.activeCallSession,
        status,
        endedAt: formatDisplayTime(),
        errorMessage,
      }

      const record: CallRecord = {
        id: session.id,
        contactId: session.contactId,
        contactName: session.contactName,
        roleView: session.roleView,
        direction: session.direction,
        status,
        startedAt: session.startedAt,
        endedAt: session.endedAt,
        durationSeconds: session.durationSeconds,
        durationLabel: formatDuration(session.durationSeconds),
        summaryStatus: 'pending',
        summaryText: session.summaryDraft,
        sdkPlan: session.sdkPlan,
      }

      this.callRecords.unshift(record)
      this.selectedCallRecordId = record.id
      this.activeCallSession = null
      this.savePersistedState()
    },
    updateCallSummary(recordId: string, summaryText: string) {
      const postCall = buildCallSummaryRisk(summaryText)

      this.callRecords = this.callRecords.map((item) =>
        item.id === recordId
          ? {
            ...item,
            summaryText,
            summaryStatus: 'uploaded',
            postCallRiskLevel: postCall.level,
            followUpAction: postCall.action,
          }
          : item,
      )

      const record = this.callRecords.find((item) => item.id === recordId)
      if (record) {
        this.upsertRiskRecord({
          id: `call-summary-${recordId}`,
          level: postCall.level,
          title: `${record.contactName} 通话后分析`,
          summary: `已根据通话摘要生成${postCall.level === 'high' ? '高' : postCall.level === 'medium' ? '中' : '低'}风险复盘建议。`,
          reason: summaryText,
          suggestion: postCall.action,
          time: formatDisplayTime(),
          source: 'call',
          confidence: postCall.level === 'high' ? 0.84 : postCall.level === 'medium' ? 0.58 : 0.22,
          traceKey: `call-summary-${recordId}`,
          detectionStatus: 'fallback',
          relatedContactId: record.contactId,
          followUpStatus: 'pending',
        })
      }

      this.selectedCallRecordId = recordId
      this.savePersistedState()
    },
    togglePriorityContact(contactId: string) {
      this.contacts = this.contacts.map((item) =>
        item.id === contactId
          ? {
            ...item,
            isPriority: !item.isPriority,
            tag: !item.isPriority ? '重点联系人' : item.tag === '重点联系人' ? undefined : item.tag,
          }
          : item,
      )
    },
    toggleBlacklistContact(contactId: string) {
      this.contacts = this.contacts.map((item) =>
        item.id === contactId
          ? {
            ...item,
            isBlacklisted: !item.isBlacklisted,
            suspiciousLevel: !item.isBlacklisted ? 'high' : item.suspiciousLevel,
            tag: !item.isBlacklisted ? '黑名单' : item.tag === '黑名单' ? undefined : item.tag,
          }
          : item,
      )
    },
    notifyCommunitySupport(elderId: string) {
      const elder = this.elders.find((item) => item.id === elderId)
      if (!elder) {
        return
      }

      this.remoteReminders.unshift({
        id: `community-${Date.now()}`,
        elderId,
        content: '已通知社区网格员跟进核验，可在必要时安排上门协助。',
        channel: 'care',
        time: formatDisplayTime(),
      })
      this.mainServiceNotice = `社区协同入口已触发，${elder.name} 的协助请求已进入待跟进状态。`
    },
    updateElderSettings(payload: Partial<ElderSettings>) {
      this.elderSettings = {
        ...this.elderSettings,
        ...payload,
      }
      this.savePersistedState()
    },
  },
})
