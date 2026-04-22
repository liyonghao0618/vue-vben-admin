<script lang="ts" setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { useAccessStore, useUserStore } from '@vben/stores';

import { Avatar, Button, Card, Modal, Space, Tag } from 'ant-design-vue';

import { useChatStore } from '#/store';

defineOptions({ name: 'ChatCallHost' });

const accessStore = useAccessStore();
const userStore = useUserStore();
const chatStore = useChatStore();
const route = useRoute();
const router = useRouter();
const remoteAudioRef = ref<HTMLAudioElement | null>(null);

function decodeJwtPayload(token: null | string) {
  if (!token) return null;
  try {
    const [, payload = ''] = token.split('.');
    if (!payload) return null;
    const normalized = payload
      .replace(/-/g, '+')
      .replace(/_/g, '/')
      .padEnd(Math.ceil(payload.length / 4) * 4, '=');
    return JSON.parse(window.atob(normalized)) as { sub?: string };
  } catch {
    return null;
  }
}

function getCurrentUserId() {
  return userStore.userInfo?.userId || decodeJwtPayload(accessStore.accessToken)?.sub || '';
}

const isIncoming = computed(() => chatStore.callPhase === 'incoming');
const isChatRoute = computed(
  () => route.name === 'ChatCenter' || route.path === '/chat/index',
);
const showCallDock = computed(
  () =>
    !isChatRoute.value &&
    ['accepting', 'calling', 'connected', 'reconnecting'].includes(
      chatStore.callPhase,
    ),
);
const callTypeLabel = computed(() =>
  chatStore.activeCall?.call_type === 'video' ? '视频' : '语音',
);
const activeConversationId = computed(
  () => chatStore.activeCall?.conversation_id || chatStore.currentConversation?.id || '',
);
const callPeerName = computed(() => {
  if (
    chatStore.currentConversation?.id &&
    chatStore.currentConversation.id === chatStore.activeCall?.conversation_id
  ) {
    return chatStore.currentConversation.peer_name || '对方';
  }
  const selfId = getCurrentUserId();
  const peer = chatStore.activeCall?.participants.find(
    (item) => item.user_id !== selfId,
  );
  return peer?.display_name || chatStore.currentConversation?.peer_name || '对方';
});
const callStatusText = computed(() => {
  if (chatStore.callPhase === 'incoming') {
    return `${callTypeLabel.value}来电`;
  }
  if (chatStore.callPhase === 'calling') {
    return `正在发起${callTypeLabel.value}通话`;
  }
  if (chatStore.callPhase === 'accepting') {
    return `正在接听${callTypeLabel.value}通话`;
  }
  if (chatStore.callPhase === 'connected') {
    return `${callTypeLabel.value}通话中`;
  }
  if (chatStore.callPhase === 'reconnecting') {
    return '网络波动，正在重连';
  }
  return '通话已结束';
});

watch(
  () => accessStore.accessToken,
  (token) => {
    if (token) {
      chatStore.connectWs();
      return;
    }
    chatStore.disconnectWs();
  },
  { immediate: true },
);

async function openChatForCall() {
  const conversationId = activeConversationId.value;
  if (!conversationId) return;
  if (
    route.path === '/chat/index' &&
    route.query.conversationId === conversationId
  ) {
    return;
  }
  await router.push({
    path: '/chat/index',
    query: {
      conversationId,
      source: 'call',
    },
  });
}

async function handleAcceptCall() {
  await openChatForCall();
  await chatStore.acceptIncomingCall();
}

async function handleBackToCall() {
  await openChatForCall();
}

function handlePageHide() {
  chatStore.flushActiveCallOnUnload('failed');
}

watch(
  () => chatStore.remoteStream,
  async (stream) => {
    await nextTick();
    if (!remoteAudioRef.value) {
      return;
    }
    remoteAudioRef.value.srcObject = stream || null;
    if (stream) {
      try {
        await remoteAudioRef.value.play();
      } catch {}
    }
  },
);

onMounted(() => {
  window.addEventListener('pagehide', handlePageHide);
  window.addEventListener('beforeunload', handlePageHide);
});

onBeforeUnmount(() => {
  window.removeEventListener('pagehide', handlePageHide);
  window.removeEventListener('beforeunload', handlePageHide);
});
</script>

<template>
  <audio ref="remoteAudioRef" autoplay playsinline class="call-audio"></audio>

  <Modal
    :open="isIncoming"
    :footer="null"
    :closable="false"
    centered
    width="420px"
  >
    <div class="incoming-modal">
      <Avatar :size="72">
        {{ callPeerName.slice(0, 1) }}
      </Avatar>
      <h3>{{ callPeerName }}</h3>
      <p>{{ callTypeLabel }}来电</p>
      <div class="incoming-actions">
        <Button danger @click="chatStore.rejectIncomingCall()">拒接</Button>
        <Button @click="chatStore.rejectIncomingCall('busy')">忙线</Button>
        <Button type="primary" @click="handleAcceptCall()">接听</Button>
      </div>
    </div>
  </Modal>

  <Card v-if="showCallDock" class="call-dock" :bordered="false">
    <div class="call-dock__header">
      <Avatar>{{ callPeerName.slice(0, 1) }}</Avatar>
      <div>
        <strong>{{ callPeerName }}</strong>
        <p>{{ callStatusText }}</p>
      </div>
    </div>
    <Space wrap>
      <Tag color="geekblue">{{ callTypeLabel }}通话</Tag>
      <Tag v-if="chatStore.callPhase === 'connected'" color="success">
        已接通
      </Tag>
    </Space>
    <div class="call-dock__actions">
      <Button type="primary" @click="handleBackToCall()">回到通话</Button>
      <Button danger @click="chatStore.endCurrentCall('ended')">挂断</Button>
    </div>
  </Card>
</template>

<style scoped>
.call-audio {
  display: none;
}

.incoming-modal {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 16px 0;
  text-align: center;
}

.incoming-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.call-dock {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 1300;
  width: min(360px, calc(100vw - 32px));
  border: 1px solid rgb(59 130 246 / 18%);
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgb(59 130 246 / 10%), transparent 30%),
    linear-gradient(180deg, rgb(255 255 255 / 96%), rgb(239 246 255 / 94%));
  box-shadow: 0 18px 40px rgb(15 23 42 / 16%);
}

.call-dock :deep(.ant-card-body) {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.call-dock__header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.call-dock__header p {
  margin: 4px 0 0;
  color: #64748b;
}

.call-dock__actions {
  display: flex;
  gap: 10px;
}

@media (max-width: 640px) {
  .incoming-actions,
  .call-dock__actions {
    flex-direction: column;
  }

  .call-dock {
    right: 16px;
    bottom: 16px;
  }
}
</style>
