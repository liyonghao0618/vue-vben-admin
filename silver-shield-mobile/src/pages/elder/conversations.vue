<template>
  <view class="page-shell">
    <ss-topbar title="聊天会话" subtitle="先看谁发来了新消息，风险消息会单独标出来。" show-back />
    <ss-voice-bar :enabled="store.elderSettings.voiceBroadcastReserved" text="会话页已预留语音播报，可朗读未读消息和风险标记。" />
    <ss-feedback-state
      v-if="store.isWeakNetwork"
      weak-network
      weak-title="当前网络不稳定"
      weak-description="会话刷新和风险识别可能延迟，建议稍后重试。"
      :hint="networkHint"
      @retry="refreshSessions"
    />
    <ss-feedback-state
      v-else-if="isLoading"
      loading
      loading-title="正在刷新会话"
      loading-description="正在同步最新消息和风险结果。"
    />
    <ss-feedback-state
      v-else-if="hasError"
      error
      error-title="会话列表刷新失败"
      error-description="风险分析暂时没有返回结果，可以重新触发刷新。"
      @retry="refreshSessions"
    />
    <ss-feedback-state
      v-else-if="!sessions.length"
      empty
      empty-title="还没有聊天会话"
      empty-description="当老人开始与家人或联系人聊天后，这里会展示最新会话。"
    />

    <ss-card v-for="session in sessions" :key="session.contactId">
      <view class="session-row" @click="openChat(session.contactId)">
        <view class="avatar">{{ session.avatarText }}</view>
        <view class="session-main">
          <view class="name-row">
            <text class="name">{{ session.name }}</text>
            <text v-if="session.tag" class="tag">{{ session.tag }}</text>
            <text v-if="session.hasRisk" class="risk-tag">风险</text>
          </view>
          <text class="relation">{{ session.relation }}</text>
          <text class="preview">{{ messageTypeLabel(session.messageType) }}{{ session.lastMessage }}</text>
        </view>
        <view class="session-side">
          <text class="time">{{ session.lastMessageTime }}</text>
          <text class="status">{{ statusLabel(session.lastMessageStatus) }}</text>
          <text v-if="session.unreadCount" class="unread">{{ session.unreadCount }}</text>
        </view>
      </view>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import SsVoiceBar from '@/components/ui/ss-voice-bar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'
import type { MessageStatus, MessageType } from '@/types/app'

const store = useAppStore()
const sessions = computed(() => store.chatSessions.filter((item) => !item.contactId.startsWith('elder-')))
const isLoading = ref(true)
const hasError = ref(false)
const networkHint = computed(() => `网络类型：${store.networkType || '未知'}，上次风险刷新：${store.lastRiskRefreshAt || '尚未刷新'}`)

onShow(() => {
  void refreshSessions()
})

async function refreshSessions() {
  isLoading.value = true
  hasError.value = false

  try {
    for (const session of sessions.value) {
      await store.refreshRiskSignals(session.contactId)
    }
  } catch {
    hasError.value = true
  } finally {
    isLoading.value = false
  }
}

function openChat(contactId: string) {
  store.selectContact(contactId)
  openPage('/pages/elder/chat')
}

function statusLabel(status: MessageStatus) {
  const map: Record<MessageStatus, string> = {
    sent: '已发送',
    received: '新消息',
    risk: '风险提醒',
  }

  return map[status]
}

function messageTypeLabel(type: MessageType) {
  if (type === 'image') {
    return '[图片] '
  }

  if (type === 'link') {
    return '[链接] '
  }

  return ''
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  background: #f7f3e9;
}
.session-row {
  display: flex;
  gap: 18rpx;
  align-items: flex-start;
}
.avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  background: #dff7f2;
  color: var(--ss-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 700;
}
.session-main {
  flex: 1;
}
.name-row {
  display: flex;
  align-items: center;
  gap: 10rpx;
  flex-wrap: wrap;
}
.name {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
.tag,
.risk-tag {
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  font-size: var(--ss-font-size-caption);
}
.tag {
  background: #fff0d2;
  color: #8a5a00;
}
.risk-tag {
  background: #fee2e2;
  color: #991b1b;
}
.relation,
.preview,
.time,
.status {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.session-side {
  min-width: 110rpx;
  text-align: right;
}
.unread {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36rpx;
  height: 36rpx;
  margin-top: 12rpx;
  padding: 0 10rpx;
  border-radius: 999rpx;
  background: var(--ss-color-danger);
  color: #fff;
  font-size: var(--ss-font-size-caption);
}
</style>
