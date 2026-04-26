import { requestClient } from '#/api/request';

export interface ChatUserSearchItem {
  user_id: string;
  username: string;
  display_name: string;
  phone: string;
  status: string;
}

export interface ChatRecommendedContactItem extends ChatUserSearchItem {
  is_emergency_contact: boolean;
  recommendation_reason: string;
  relationship_type?: null | string;
  source: string;
}

export interface ChatConversationItem {
  id: string;
  conversation_type: string;
  title: string;
  peer_user_id?: null | string;
  peer_name?: null | string;
  peer_status?: null | string;
  unread_count: number;
  last_message_preview?: null | string;
  last_message_at?: null | string;
  last_message_id?: null | string;
}

export interface ChatConversationMemberItem {
  user_id: string;
  display_name: string;
  status: string;
  joined_at?: null | string;
  last_read_message_id?: null | string;
  last_read_at?: null | string;
  unread_count: number;
}

export interface ChatMessageItem {
  id: string;
  conversation_id: string;
  sender_user_id: string;
  sender_name: string;
  message_type: string;
  content_text: string;
  content_json?: null | Record<string, any>;
  status: string;
  is_self: boolean;
  delivered_at?: null | string;
  read_by_all_at?: null | string;
  risk_level: 'high' | 'low' | 'medium' | string;
  risk_category?: null | string;
  risk_reason?: null | string;
  risk_suggestion?: null | string;
  created_at: string;
}

export interface CallParticipantItem {
  user_id: string;
  display_name: string;
  role: string;
  join_state: string;
  joined_at?: null | string;
  left_at?: null | string;
}

export interface CallEventItem {
  id: string;
  call_session_id: string;
  actor_user_id?: null | string;
  event_type: string;
  payload_json?: null | Record<string, any>;
  created_at: string;
}

export interface CallSessionItem {
  id: string;
  conversation_id: string;
  initiator_user_id: string;
  receiver_user_id: string;
  call_type: 'audio' | 'video' | string;
  status: string;
  started_at?: null | string;
  answered_at?: null | string;
  ended_at?: null | string;
  ended_reason?: null | string;
  duration_seconds: number;
  participants: CallParticipantItem[];
  events: CallEventItem[];
}

export interface ChatConversationDetail extends ChatConversationItem {
  members: ChatConversationMemberItem[];
  messages: ChatMessageItem[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
  };
}

export interface OnlineStateItem {
  user_id: string;
  is_online: boolean;
  last_seen_at?: null | string;
  client_type?: null | string;
}

export async function searchChatUsersApi(keyword?: string) {
  return requestClient.get<ChatUserSearchItem[]>('/chats/users/search', {
    params: { keyword },
  });
}

export async function getChatRecommendedContactsApi(limit = 10) {
  return requestClient.get<ChatRecommendedContactItem[]>(
    '/chats/users/recommendations',
    {
      params: { limit },
    },
  );
}

export async function createChatConversationApi(participantUserId: string) {
  return requestClient.post<ChatConversationDetail>('/chats/conversations', {
    conversation_type: 'direct',
    participant_user_ids: [participantUserId],
  });
}

export async function getChatConversationListApi() {
  return requestClient.get<ChatConversationItem[]>('/chats/conversations');
}

export async function getChatConversationDetailApi(
  conversationId: string,
  page = 1,
  pageSize = 50,
) {
  return requestClient.get<ChatConversationDetail>(
    `/chats/conversations/${conversationId}`,
    {
      params: { page, page_size: pageSize },
    },
  );
}

export async function sendChatMessageApi(
  conversationId: string,
  contentText: string,
) {
  return requestClient.post<ChatMessageItem>(
    `/chats/conversations/${conversationId}/messages`,
    {
      content_text: contentText,
      message_type: 'text',
    },
  );
}

export async function markChatReadApi(
  conversationId: string,
  lastReadMessageId: string,
) {
  return requestClient.post<{ total_unread: number }>(
    `/chats/conversations/${conversationId}/read`,
    {
      last_read_message_id: lastReadMessageId,
    },
  );
}

export async function getChatUnreadSummaryApi() {
  return requestClient.get<{ total_unread: number }>('/chats/unread-summary');
}

export async function getChatOnlineStatesApi(userIds: string[]) {
  return requestClient.get<OnlineStateItem[]>('/chats/online-states', {
    params: { user_ids: userIds },
    paramsSerializer: 'repeat',
  });
}

export async function createCallSessionApi(
  conversationId: string,
  callType: 'audio' | 'video',
) {
  return requestClient.post<CallSessionItem>('/chats/calls', {
    conversation_id: conversationId,
    call_type: callType,
  });
}

export async function getCallSessionDetailApi(callSessionId: string) {
  return requestClient.get<CallSessionItem>(`/chats/calls/${callSessionId}`);
}

export async function getCallHistoryApi(conversationId?: string) {
  return requestClient.get<CallSessionItem[]>('/chats/calls', {
    params: { conversation_id: conversationId },
  });
}

export async function endCallSessionApi(
  callSessionId: string,
  reason: 'busy' | 'cancelled' | 'ended' | 'failed' | 'missed' | 'rejected' | 'timeout',
) {
  return requestClient.post<CallSessionItem>(`/chats/calls/${callSessionId}/end`, {
    reason,
  });
}

export async function sendCallSignalApi(
  event: CallSignalEventRequest['event'],
  callSessionId: string,
  data?: Record<string, any>,
) {
  return requestClient.post<CallSessionItem>('/chats/calls/signal', {
    event,
    call_session_id: callSessionId,
    data,
  });
}

export interface CallAudioRecognitionResult {
  alert_id?: null | string;
  hit_rule_codes: string[];
  hit_terms: string[];
  notification_ids: string[];
  reason_detail: string;
  record_id: string;
  risk_level: 'high' | 'low' | 'medium' | string;
  risk_score: number;
  scene: string;
  suggestion_action: string;
  workorder_id?: null | string;
}

export async function uploadCallAudioRecognitionApi(payload: {
  audioFile: Blob;
  callSessionId?: null | string;
  callerNumber?: null | string;
  durationSeconds?: number;
  elderUserId: string;
  filename?: string;
  occurredAt?: null | string;
}) {
  const formData = new FormData();
  formData.append(
    'audio_file',
    payload.audioFile,
    payload.filename || 'call-audio.webm',
  );
  formData.append('elder_user_id', payload.elderUserId);
  if (payload.callSessionId) formData.append('call_session_id', payload.callSessionId);
  if (payload.callerNumber) formData.append('caller_number', payload.callerNumber);
  if (typeof payload.durationSeconds === 'number') {
    formData.append('duration_seconds', String(payload.durationSeconds));
  }
  if (payload.occurredAt) formData.append('occurred_at', payload.occurredAt);

  return requestClient.post<CallAudioRecognitionResult>(
    '/risk-recognition/call-audio',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 240_000,
    },
  );
}

export interface CallSignalEventRequest {
  event:
    | 'call.accept'
    | 'call.answer'
    | 'call.busy'
    | 'call.end'
    | 'call.ice-candidate'
    | 'call.offer'
    | 'call.reject'
    | 'call.ringing'
    | 'call.timeout';
  call_session_id: string;
  data?: Record<string, any>;
}
