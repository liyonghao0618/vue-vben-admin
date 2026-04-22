<script lang="ts" setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import { useUserStore } from '@vben/stores';

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

import { useChatStore } from '#/store';

defineOptions({ name: 'ChatCenter' });

const chatStore = useChatStore();
const userStore = useUserStore();
const route = useRoute();

const keyword = ref('');
const draft = ref('');
const pendingRouteTarget = ref('');
const localVideoRef = ref<HTMLVideoElement | null>(null);
const remoteVideoRef = ref<HTMLVideoElement | null>(null);

const currentMessages = computed(
  () => chatStore.currentConversation?.messages ?? [],
);

const currentPeerOnline = computed(() => {
  const peerId = chatStore.currentConversation?.peer_user_id;
  return peerId ? chatStore.onlineStates[peerId]?.is_online : false;
});

const isInCall = computed(() =>
  ['accepting', 'calling', 'connected', 'incoming', 'reconnecting'].includes(
    chatStore.callPhase,
  ),
);
const callDurationText = computed(() => {
  const minutes = Math.floor(chatStore.callSeconds / 60)
    .toString()
    .padStart(2, '0');
  const seconds = (chatStore.callSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
});

function getRiskMeta(level: string) {
  if (level === 'high') return { color: 'red', text: '高风险提醒' };
  if (level === 'medium') return { color: 'orange', text: '谨慎提醒' };
  return { color: 'green', text: '正常' };
}

function getCallStatusText() {
  const typeText = chatStore.activeCall?.call_type === 'video' ? '视频' : '语音';
  if (chatStore.callPhase === 'incoming') return `来电响铃中 · ${typeText}通话`;
  if (chatStore.callPhase === 'calling') return `正在呼叫对方 · ${typeText}通话`;
  if (chatStore.callPhase === 'accepting') return '正在接听，建立媒体协商...';
  if (chatStore.callPhase === 'connected') return `通话中 ${callDurationText.value}`;
  if (chatStore.callPhase === 'reconnecting') return '网络波动，正在重连...';
  return '通话已结束';
}

function getCallCardText(message: any) {
  const payload = message.content_json || {};
  const reasonMap: Record<string, string> = {
    busy: '对方忙线',
    cancelled: '已取消',
    ended: `通话 ${formatDuration(payload.duration_seconds || 0)}`,
    failed: '通话失败',
    missed: '未接来电',
    rejected: '已拒接',
    timeout: '呼叫超时',
  };
  return reasonMap[payload.ended_reason || payload.status] || message.content_text;
}

function formatDuration(totalSeconds: number) {
  const minutes = Math.floor(totalSeconds / 60)
    .toString()
    .padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
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

async function handleStartCall(callType: 'audio' | 'video') {
  await chatStore.startCall(callType);
}

async function handleRedialFromCard(message: any) {
  const callType = message.content_json?.call_type === 'video' ? 'video' : 'audio';
  await chatStore.startCall(callType);
}

async function syncRouteIntent() {
  const conversationId =
    typeof route.query.conversationId === 'string'
      ? route.query.conversationId
      : '';
  const targetUserId = typeof route.query.userId === 'string' ? route.query.userId : '';
  const routeKey = conversationId || targetUserId;
  if (!routeKey || pendingRouteTarget.value === routeKey) {
    return;
  }
  pendingRouteTarget.value = routeKey;
  if (conversationId) {
    await chatStore.openConversation(conversationId);
    return;
  }
  await chatStore.startConversation(targetUserId);
}

watch(draft, (value) => {
  if (value.trim()) {
    chatStore.sendTyping();
  }
});

watch(
  () => [route.query.conversationId, route.query.userId],
  () => {
    void syncRouteIntent();
  },
  { immediate: false },
);

watch(
  () => chatStore.localStream,
  async (stream) => {
    await nextTick();
    if (localVideoRef.value) {
      localVideoRef.value.srcObject = stream || null;
    }
  },
);

watch(
  () => chatStore.remoteStream,
  async (stream) => {
    await nextTick();
    if (remoteVideoRef.value) {
      remoteVideoRef.value.srcObject = stream || null;
    }
  },
);

onMounted(async () => {
  chatStore.connectWs();
  await chatStore.loadConversations();
  await syncRouteIntent();
});
</script>

<template>
  <div class="chat-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">站内 IM / 反诈协同 / WebRTC</p>
        <h1>实时聊天与电话中心</h1>
        <p class="description">
          支持站内实时聊天、通话信令和一对一音视频协同，在风险对话中可以快速切换到语音或视频确认。
        </p>
      </div>
      <Space wrap>
        <Tag color="processing">当前用户：{{ userStore.userInfo?.realName }}</Tag>
        <Tag color="blue">总未读 {{ chatStore.totalUnread }}</Tag>
        <Tag color="geekblue">
          {{ isInCall ? getCallStatusText() : '当前无进行中通话' }}
        </Tag>
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
          <p class="section-title">推荐联系人</p>
          <List
            size="small"
            :data-source="chatStore.recommendedContacts"
            :locale="{ emptyText: '当前暂无绑定关系推荐联系人' }"
          >
            <template #renderItem="{ item }">
              <List.Item class="user-item">
                <div>
                  <strong>
                    {{ item.display_name }}
                    <Tag v-if="item.is_emergency_contact" color="red">紧急联系人</Tag>
                  </strong>
                  <p>{{ item.recommendation_reason }}</p>
                </div>
                <Button size="small" @click="handleStartChat(item.user_id)">
                  快速发起
                </Button>
              </List.Item>
            </template>
          </List>

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
            <Space wrap>
              <Button
                :disabled="!currentPeerOnline && !chatStore.currentConversation.peer_user_id"
                @click="handleStartCall('audio')"
              >
                语音呼叫
              </Button>
              <Button type="primary" @click="handleStartCall('video')">
                视频呼叫
              </Button>
            </Space>
          </div>

          <div v-if="isInCall" class="call-panel">
            <div class="call-stage">
              <div class="call-meta">
                <p class="call-title">
                  {{ chatStore.currentConversation.peer_name }}
                </p>
                <p class="call-status">{{ getCallStatusText() }}</p>
                <p v-if="chatStore.callError" class="call-error">{{ chatStore.callError }}</p>
                <p
                  v-if="chatStore.permissionState === 'denied'"
                  class="call-error"
                >
                  浏览器已拒绝设备权限，当前无法建立音视频通话。
                </p>
              </div>
              <div
                v-if="chatStore.activeCall?.call_type === 'video'"
                class="video-grid"
              >
                <video
                  ref="remoteVideoRef"
                  autoplay
                  muted
                  playsinline
                  class="remote-video"
                ></video>
                <video
                  ref="localVideoRef"
                  autoplay
                  muted
                  playsinline
                  class="local-video"
                ></video>
              </div>
              <div v-else class="audio-visual">
                <Avatar :size="84">
                  {{ (chatStore.currentConversation.peer_name || '').slice(0, 1) }}
                </Avatar>
                <div>
                  <strong>语音通话中</strong>
                  <p>可随时切换到视频，或保持纯语音沟通。</p>
                </div>
              </div>
            </div>

            <div class="call-actions">
              <Button @click="chatStore.toggleAudio()">
                {{ chatStore.localAudioEnabled ? '静音' : '取消静音' }}
              </Button>
              <Button @click="chatStore.toggleVideo()">
                {{ chatStore.localVideoEnabled ? '关闭视频' : '打开视频' }}
              </Button>
              <Button danger @click="chatStore.endCurrentCall('ended')">挂断</Button>
            </div>
          </div>

          <div class="message-list">
            <div
              v-for="item in currentMessages"
              :key="item.id"
              class="message-row" :class="[item.is_self ? 'self' : 'peer']"
            >
              <div
                v-if="item.message_type === 'card' && item.content_json?.card_type === 'call_record'"
                class="message-bubble call-record-card"
              >
                <p class="meta">
                  {{ item.sender_name }} ·
                  {{ new Date(item.created_at).toLocaleString() }}
                </p>
                <strong>
                  {{ item.content_json.call_type === 'video' ? '视频通话' : '语音通话' }}
                </strong>
                <p class="text">{{ getCallCardText(item) }}</p>
                <div class="bubble-footer">
                  <Tag color="blue">通话记录</Tag>
                  <Button size="small" @click="handleRedialFromCard(item)">
                    重新拨打
                  </Button>
                </div>
              </div>

              <div v-else class="message-bubble">
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
              <span>
                文本消息、语音/视频通话、通话记录回拨已接入当前聊天页。
              </span>
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
    radial-gradient(circle at top left, rgba(245, 158, 11, 0.18), transparent 34%),
    radial-gradient(circle at bottom right, rgba(45, 212, 191, 0.18), transparent 34%),
    linear-gradient(135deg, #0f172a, #0f766e 55%, #0f172a);
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
.meta,
.call-status {
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

.call-panel {
  margin-bottom: 16px;
  padding: 18px;
  border: 1px solid #dbeafe;
  border-radius: 22px;
  background:
    linear-gradient(135deg, rgba(219, 234, 254, 0.9), rgba(240, 249, 255, 0.92));
}

.call-stage {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.call-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
}

.call-error {
  color: #b91c1c;
}

.video-grid {
  position: relative;
  min-height: 280px;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, #0f172a, #1e293b);
}

.remote-video,
.local-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #0f172a;
}

.local-video {
  position: absolute;
  right: 16px;
  bottom: 16px;
  width: 160px;
  height: 120px;
  border: 2px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
}

.audio-visual {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.7);
}

.call-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
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

.call-record-card {
  border: 1px solid #bfdbfe;
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
  .composer-actions,
  .call-actions,
  .audio-visual {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: stretch;
  }

  .chat-layout {
    display: flex;
    flex-direction: column;
  }

  .local-video {
    width: 108px;
    height: 144px;
    right: 12px;
    bottom: 12px;
  }
}
</style>
