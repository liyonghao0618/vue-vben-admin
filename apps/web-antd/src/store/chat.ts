import { ref } from 'vue';

import { useAccessStore, useUserStore } from '@vben/stores';

import { defineStore } from 'pinia';

import type {
  ChatConversationDetail,
  ChatConversationItem,
  ChatMessageItem,
  ChatUserSearchItem,
  OnlineStateItem,
} from '#/api';
import {
  createChatConversationApi,
  getChatConversationDetailApi,
  getChatConversationListApi,
  getChatOnlineStatesApi,
  getChatUnreadSummaryApi,
  markChatReadApi,
  searchChatUsersApi,
  sendChatMessageApi,
} from '#/api';

function buildChatWsUrl(token: string) {
  const apiBase = import.meta.env.VITE_GLOB_API_URL || window.location.origin;
  const url = new URL(apiBase, window.location.origin);
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  url.pathname = '/api/v1/chats/ws';
  url.searchParams.set('token', token);
  return url.toString();
}

export const useChatStore = defineStore('chat', () => {
  const accessStore = useAccessStore();
  const userStore = useUserStore();

  const conversations = ref<ChatConversationItem[]>([]);
  const currentConversation = ref<ChatConversationDetail | null>(null);
  const searchResults = ref<ChatUserSearchItem[]>([]);
  const totalUnread = ref(0);
  const onlineStates = ref<Record<string, OnlineStateItem>>({});
  const typingText = ref('');
  const sending = ref(false);
  const connecting = ref(false);
  const socket = ref<null | WebSocket>(null);

  async function loadConversations() {
    conversations.value = await getChatConversationListApi();
    totalUnread.value = (await getChatUnreadSummaryApi()).total_unread;
    await refreshOnlineStates();
  }

  async function searchUsers(keyword: string) {
    searchResults.value = keyword ? await searchChatUsersApi(keyword) : [];
  }

  async function openConversation(conversationId: string) {
    currentConversation.value = await getChatConversationDetailApi(conversationId);
    const lastMessage = currentConversation.value.messages.at(-1);
    if (lastMessage && !lastMessage.is_self) {
      const summary = await markChatReadApi(conversationId, lastMessage.id);
      totalUnread.value = summary.total_unread;
    }
  }

  async function startConversation(userId: string) {
    const detail = await createChatConversationApi(userId);
    currentConversation.value = detail;
    await loadConversations();
  }

  async function sendMessage(content: string) {
    if (!currentConversation.value || !content.trim()) return;
    sending.value = true;
    try {
      const message = await sendChatMessageApi(currentConversation.value.id, content);
      mergeMessage(message);
      await loadConversations();
    } finally {
      sending.value = false;
    }
  }

  function mergeMessage(message: ChatMessageItem) {
    if (currentConversation.value?.id !== message.conversation_id) return;
    const exists = currentConversation.value.messages.some((item) => item.id === message.id);
    if (!exists) {
      currentConversation.value.messages.push(message);
    }
  }

  async function refreshOnlineStates() {
    const ids = conversations.value
      .map((item) => item.peer_user_id)
      .filter((item): item is string => Boolean(item));
    if (!ids.length) return;
    const rows = await getChatOnlineStatesApi(ids);
    onlineStates.value = Object.fromEntries(rows.map((item) => [item.user_id, item]));
  }

  function connectWs() {
    const token = accessStore.accessToken;
    if (!token || socket.value) return;
    connecting.value = true;
    const ws = new WebSocket(buildChatWsUrl(token));
    ws.onopen = () => {
      connecting.value = false;
      socket.value = ws;
      ws.send(JSON.stringify({ event: 'ping' }));
    };
    ws.onmessage = async (event) => {
      const payload = JSON.parse(event.data);
      if (payload.event === 'message') {
        mergeMessage(payload.data as ChatMessageItem);
        await loadConversations();
      }
      if (payload.event === 'typing') {
        if (payload.data.user_id !== userStore.userInfo?.userId) {
          typingText.value = `${payload.data.display_name} 正在输入...`;
          setTimeout(() => {
            typingText.value = '';
          }, 1500);
        }
      }
      if (payload.event === 'read' && currentConversation.value) {
        currentConversation.value.messages = currentConversation.value.messages.map((item) =>
          item.id === payload.data.last_read_message_id
            ? { ...item, read_by_all_at: new Date().toISOString() }
            : item,
        );
        totalUnread.value = payload.data.total_unread ?? totalUnread.value;
      }
    };
    ws.onclose = () => {
      socket.value = null;
      connecting.value = false;
      setTimeout(() => {
        connectWs();
      }, 2000);
    };
  }

  function sendTyping() {
    if (!socket.value || !currentConversation.value) return;
    socket.value.send(
      JSON.stringify({
        event: 'typing',
        data: {
          conversation_id: currentConversation.value.id,
        },
      }),
    );
  }

  return {
    connectWs,
    connecting,
    conversations,
    currentConversation,
    loadConversations,
    onlineStates,
    openConversation,
    refreshOnlineStates,
    searchResults,
    searchUsers,
    sendMessage,
    sendTyping,
    sending,
    startConversation,
    totalUnread,
    typingText,
  };
});
