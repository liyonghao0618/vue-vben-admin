<script lang="ts" setup>
import { computed, onMounted, ref, watch } from 'vue';

import {
  Avatar,
  Badge,
  Button,
  Card,
  Empty,
  Input,
  List,
  Space,
  Tag,
} from 'ant-design-vue';

import { useUserStore } from '@vben/stores';

import { useChatStore } from '#/store';

defineOptions({ name: 'ChatCenter' });

const chatStore = useChatStore();
const userStore = useUserStore();

const keyword = ref('');
const draft = ref('');

const currentMessages = computed(
  () => chatStore.currentConversation?.messages ?? [],
);

const currentPeerOnline = computed(() => {
  const peerId = chatStore.currentConversation?.peer_user_id;
  return peerId ? chatStore.onlineStates[peerId]?.is_online : false;
});

function getRiskMeta(level: string) {
  if (level === 'high') return { color: 'red', text: '高风险提醒' };
  if (level === 'medium') return { color: 'orange', text: '谨慎提醒' };
  return { color: 'green', text: '正常' };
}

async function handleSearch() {
  await chatStore.searchUsers(keyword.value);
}

async function handleStartChat(userId: string) {
  await chatStore.startConversation(userId);
}

async function handleOpenConversation(conversationId: string) {
  await chatStore.openConversation(conversationId);
}

async function handleSend() {
  const content = draft.value.trim();
  if (!content) return;
  draft.value = '';
  await chatStore.sendMessage(content);
}

watch(draft, (value) => {
  if (value.trim()) {
    chatStore.sendTyping();
  }
});

onMounted(async () => {
  chatStore.connectWs();
  await chatStore.loadConversations();
});
</script>

<template>
  <div class="chat-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">站内 IM / 反诈协同</p>
        <h1>实时聊天中心</h1>
        <p class="description">
          支持系统内任意可达用户发起点对点聊天，文本消息会实时同步，并对高风险话术、链接和转账诱导进行即时提醒。
        </p>
      </div>
      <Space>
        <Tag color="processing">当前用户：{{ userStore.userInfo?.realName }}</Tag>
        <Tag color="blue">总未读 {{ chatStore.totalUnread }}</Tag>
      </Space>
    </section>

    <div class="chat-layout">
      <Card class="sidebar-card" :bordered="false">
        <div class="search-box">
          <Input
            v-model:value="keyword"
            placeholder="搜索用户昵称、账号、手机号"
            @press-enter="handleSearch"
          />
          <Button type="primary" @click="handleSearch">搜索</Button>
        </div>

        <div class="search-results">
          <p class="section-title">发起聊天</p>
          <List
            size="small"
            :data-source="chatStore.searchResults"
            :locale="{ emptyText: '输入关键词后可发起新会话' }"
          >
            <template #renderItem="{ item }">
              <List.Item class="user-item">
                <div>
                  <strong>{{ item.display_name }}</strong>
                  <p>{{ item.username }} · {{ item.phone }}</p>
                </div>
                <Button size="small" @click="handleStartChat(item.user_id)">
                  发消息
                </Button>
              </List.Item>
            </template>
          </List>
        </div>

        <div class="conversation-list">
          <p class="section-title">会话列表</p>
          <List
            :data-source="chatStore.conversations"
            :locale="{ emptyText: '暂无会话，可先搜索用户发起聊天' }"
          >
            <template #renderItem="{ item }">
              <List.Item
                class="conversation-item"
                @click="handleOpenConversation(item.id)"
              >
                <Badge :count="item.unread_count" :offset="[-6, 8]">
                  <Avatar>{{ (item.peer_name || item.title).slice(0, 1) }}</Avatar>
                </Badge>
                <div class="conversation-main">
                  <div class="conversation-top">
                    <strong>{{ item.peer_name || item.title }}</strong>
                    <Tag
                      v-if="item.peer_user_id && chatStore.onlineStates[item.peer_user_id]?.is_online"
                      color="success"
                    >
                      在线
                    </Tag>
                  </div>
                  <p>{{ item.last_message_preview || '还没有消息' }}</p>
                </div>
              </List.Item>
            </template>
          </List>
        </div>
      </Card>

      <Card class="chat-card" :bordered="false">
        <template v-if="chatStore.currentConversation">
          <div class="chat-header">
            <div>
              <h2>{{ chatStore.currentConversation.peer_name }}</h2>
              <p>
                {{ currentPeerOnline ? '当前在线' : '当前离线' }}
                <span v-if="chatStore.typingText"> · {{ chatStore.typingText }}</span>
              </p>
            </div>
            <Space>
              <Tag color="gold">图片/语音/文件位</Tag>
              <Tag color="cyan">通话入口预留</Tag>
            </Space>
          </div>

          <div class="message-list">
            <div
              v-for="item in currentMessages"
              :key="item.id"
              :class="['message-row', item.is_self ? 'self' : 'peer']"
            >
              <div class="message-bubble">
                <p class="meta">
                  {{ item.sender_name }} ·
                  {{ new Date(item.created_at).toLocaleString() }}
                </p>
                <p class="text">{{ item.content_text }}</p>
                <div class="bubble-footer">
                  <Tag :color="getRiskMeta(item.risk_level).color">
                    {{ getRiskMeta(item.risk_level).text }}
                  </Tag>
                  <span v-if="item.read_by_all_at">已读</span>
                  <span v-else>已送达</span>
                </div>
                <div
                  v-if="item.risk_level !== 'low' && (item.risk_reason || item.risk_suggestion)"
                  class="risk-box"
                >
                  <strong>反诈 AI 提醒</strong>
                  <p>{{ item.risk_reason }}</p>
                  <p>{{ item.risk_suggestion }}</p>
                  <div class="risk-actions">
                    <Button danger size="small">求助入口</Button>
                    <Button size="small">确认风险</Button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="composer">
            <Input.TextArea
              v-model:value="draft"
              :auto-size="{ minRows: 3, maxRows: 5 }"
              placeholder="输入消息内容，若包含链接、验证码或转账话术会触发风险提醒"
            />
            <div class="composer-actions">
              <span>一期仅支持文字消息，已为多模态与通话入口预留交互位。</span>
              <Button
                type="primary"
                :loading="chatStore.sending"
                @click="handleSend"
              >
                发送
              </Button>
            </div>
          </div>
        </template>

        <Empty
          v-else
          description="请选择一个会话，或先搜索用户发起聊天。"
        />
      </Card>
    </div>
  </div>
</template>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 24px;
  border-radius: 24px;
  background:
    radial-gradient(circle at top left, rgba(245, 158, 11, 0.22), transparent 35%),
    linear-gradient(135deg, #0f172a, #1d4ed8 55%, #0f766e);
  color: #fff;
}

.eyebrow {
  margin-bottom: 8px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  opacity: 0.75;
}

.description {
  max-width: 720px;
  opacity: 0.9;
}

.chat-layout {
  display: grid;
  grid-template-columns: 340px minmax(0, 1fr);
  gap: 16px;
}

.sidebar-card,
.chat-card {
  border-radius: 24px;
}

.search-box {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  margin-bottom: 16px;
}

.section-title {
  margin: 0 0 8px;
  color: #64748b;
  font-size: 13px;
}

.user-item,
.conversation-item {
  cursor: pointer;
}

.conversation-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  padding: 10px 0;
}

.conversation-main {
  min-width: 0;
}

.conversation-top {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.conversation-main p,
.user-item p,
.chat-header p,
.meta {
  margin: 0;
  color: #64748b;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 420px;
  max-height: 60vh;
  padding: 8px 0 16px;
  overflow: auto;
}

.message-row {
  display: flex;
}

.message-row.self {
  justify-content: flex-end;
}

.message-bubble {
  width: min(100%, 640px);
  padding: 14px 16px;
  border-radius: 18px;
  background: #f8fafc;
}

.message-row.self .message-bubble {
  background: linear-gradient(135deg, #dbeafe, #eff6ff);
}

.text {
  margin: 8px 0 0;
  white-space: pre-wrap;
  color: #0f172a;
}

.bubble-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 10px;
}

.risk-box {
  margin-top: 12px;
  padding: 12px;
  border-radius: 14px;
  background: #fff7ed;
  border: 1px solid #fdba74;
}

.risk-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.composer {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 16px;
}

.composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #64748b;
  font-size: 13px;
}

@media (max-width: 960px) {
  .hero-panel,
  .chat-layout,
  .chat-header,
  .composer-actions {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: stretch;
  }

  .chat-layout {
    display: flex;
    flex-direction: column;
  }
}
</style>
