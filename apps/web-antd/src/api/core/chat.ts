import { requestClient } from '#/api/request';

export interface ChatUserSearchItem {
  user_id: string;
  username: string;
  display_name: string;
  phone: string;
  status: string;
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
  });
}
