<template>
  <view class="page-shell">
    <ss-topbar title="会话列表" subtitle="优先查看带风险标记和未读消息的老人会话。" show-back />

    <ss-feedback-state
      v-if="!sessions.length"
      empty
      empty-title="当前还没有老人会话"
      empty-description="发送提醒、回访消息或同步图片 OCR 结果后，这里会展示最新会话。"
    />

    <ss-card v-for="session in sessions" :key="session.contactId">
      <view class="session-row" @click="openChat(session.contactId)">
        <view class="avatar">{{ session.avatarText }}</view>
        <view class="session-main">
          <view class="name-row">
            <text class="name">{{ session.name }}</text>
            <text v-if="session.tag" class="tag">{{ session.tag }}</text>
            <text v-if="session.hasRisk" class="risk-tag">风险</text>
            <text v-if="isPriority(session.contactId)" class="tag priority">重点</text>
            <text v-if="isBlacklisted(session.contactId)" class="risk-tag">黑名单</text>
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
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'
import type { MessageStatus, MessageType } from '@/types/app'

const store = useAppStore()
const sessions = computed(() => store.chatSessions.filter((item) => item.contactId.startsWith('elder-')))

function openChat(contactId: string) {
  store.selectElder(contactId)
  openPage('/pages/guardian/chat')
}

function isPriority(contactId: string) {
  return Boolean(store.contacts.find((item) => item.id === contactId)?.isPriority)
}

function isBlacklisted(contactId: string) {
  return Boolean(store.contacts.find((item) => item.id === contactId)?.isBlacklisted)
}

function statusLabel(status: MessageStatus) {
  const map: Record<MessageStatus, string> = {
    sent: '已发送',
    received: '新消息',
    risk: '风险同步',
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
  background: #eef4f6;
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
  font-size: 31rpx;
  font-weight: 700;
}
.tag,
.risk-tag {
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  font-size: 20rpx;
}
.tag {
  background: #fff0d2;
  color: #8a5a00;
}
.tag.priority {
  background: #dff7f2;
  color: var(--ss-color-primary);
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
  font-size: 24rpx;
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
  font-size: 20rpx;
}
</style>
