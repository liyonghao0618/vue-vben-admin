export type UserRole = 'elder' | 'guardian'
export type RiskLevel = 'low' | 'medium' | 'high'
export type MessageSender = 'self' | 'other' | 'system'
export type MessageStatus = 'sent' | 'received' | 'risk'
export type MessageType = 'text' | 'image' | 'link'
export type CallDirection = 'incoming' | 'outgoing'
export type CallStatus = 'idle' | 'ringing' | 'connecting' | 'connected' | 'ended' | 'failed' | 'missed' | 'rejected'
export type NetworkStatus = 'unknown' | 'offline' | 'weak' | 'online'

export interface RoleCard {
  role: UserRole
  title: string
  subtitle: string
  points: string[]
  cta: string
}

export interface RiskRecord {
  id: string
  level: RiskLevel
  title: string
  summary: string
  reason?: string
  suggestion?: string
  time?: string
  source?: 'chat' | 'link' | 'call' | 'manual'
  matchedText?: string[]
  confidence?: number
  traceKey?: string
  detectionStatus?: 'success' | 'fallback'
  relatedContactId?: string
  followUpStatus?: 'pending' | 'processing' | 'resolved'
}

export interface Contact {
  id: string
  name: string
  relation: string
  avatarText: string
  isGuardian?: boolean
  tag?: string
  note?: string
  isPriority?: boolean
  suspiciousLevel?: RiskLevel | 'none'
  isBlacklisted?: boolean
  supportsCommunityAssist?: boolean
}

export interface ElderProfile {
  id: string
  name: string
  age: number
  relation: string
  statusSummary: string
  lastContactAt: string
  lastRiskAt?: string
  riskLevel: RiskLevel
  riskCountToday: number
  pendingAlerts: number
  hasActiveSos?: boolean
  medicationNote?: string
}

export interface ChatMessage {
  id: string
  contactId: string
  sender: MessageSender
  type: MessageType
  content: string
  time: string
  status: MessageStatus
  riskLevel?: RiskLevel
  suspicious?: boolean
  riskReason?: string
  previewImageUrl?: string
  linkUrl?: string
  linkTitle?: string
  ocrStatus?: 'pending' | 'done'
  ocrText?: string
}

export interface ChatSession {
  contactId: string
  name: string
  relation: string
  avatarText: string
  tag?: string
  lastMessage: string
  lastMessageTime: string
  lastMessageStatus: MessageStatus
  unreadCount: number
  hasRisk: boolean
  messageType: MessageType
}

export interface RemoteReminder {
  id: string
  elderId: string
  content: string
  channel: 'chat' | 'care'
  time: string
}

export interface SosAlert {
  id: string
  elderId: string
  elderName: string
  summary: string
  status: 'pending' | 'processing' | 'resolved'
  time: string
  detail?: string
  location?: string
  linkedTicketNo?: string
  latestAction?: string
  reporterPhone?: string
  detectionStatus?: 'success' | 'fallback'
}

export interface CallRecord {
  id: string
  contactId: string
  contactName: string
  roleView: UserRole
  direction: CallDirection
  status: Exclude<CallStatus, 'idle' | 'ringing' | 'connecting' | 'connected'>
  startedAt: string
  endedAt?: string
  durationSeconds: number
  durationLabel: string
  summaryStatus: 'pending' | 'uploaded'
  summaryText?: string
  sdkPlan: string
  postCallRiskLevel?: RiskLevel
  followUpAction?: string
}

export interface ActiveCallSession {
  id: string
  contactId: string
  contactName: string
  relation: string
  avatarText: string
  roleView: UserRole
  direction: CallDirection
  status: Exclude<CallStatus, 'idle'>
  startedAt: string
  connectedAt?: string
  endedAt?: string
  durationSeconds: number
  sdkPlan: string
  summaryDraft: string
  errorMessage?: string
}

export interface ElderSettings {
  fontScale: 'large' | 'x-large'
  contrastMode: boolean
  voiceBroadcastReserved: boolean
  simplifyMode: boolean
}

export interface UserProfile {
  id: string
  name: string
  role: UserRole
  phone: string
  welcomeText: string
}

export interface LoginForm {
  account: string
  password: string
  role: UserRole
}

export interface RiskTrendPoint {
  label: string
  high: number
  medium: number
  low: number
}
