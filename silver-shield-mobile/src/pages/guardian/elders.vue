<template>
  <view class="page-shell">
    <ss-topbar title="老人列表" subtitle="先看谁有风险、谁刚发来求助，再进入聊天回访。" show-back />
    <ss-feedback-state
      v-if="!elders.length"
      empty
      empty-title="当前没有可查看的老人"
      empty-description="完成绑定关系和用户信息联调后，这里会展示监护中的老人列表。"
    />

    <ss-card v-for="elder in elders" :key="elder.id">
      <view class="elder-row">
        <view class="avatar">{{ elder.name.slice(0, 1) }}</view>
        <view class="elder-main">
          <view class="name-row">
            <text class="name">{{ elder.name }}</text>
            <text class="risk-tag" :class="elder.riskLevel">{{ levelTextMap[elder.riskLevel] }}</text>
            <text v-if="isPriority(elder.id)" class="risk-tag low">重点联系人</text>
            <text v-if="isBlacklisted(elder.id)" class="risk-tag high">黑名单</text>
          </view>
          <text class="meta">{{ elder.relation }} · {{ elder.age }} 岁</text>
          <text class="summary">{{ elder.statusSummary }}</text>
          <text class="summary">最近联系：{{ elder.lastContactAt }}</text>
          <text v-if="elder.medicationNote" class="summary">关怀提醒：{{ elder.medicationNote }}</text>
        </view>
      </view>

      <view class="metrics-row">
        <text class="metric">今日风险 {{ elder.riskCountToday }}</text>
        <text class="metric">待处理 {{ elder.pendingAlerts }}</text>
        <text class="metric">{{ elder.hasActiveSos ? '有求助待回访' : '当前无求助' }}</text>
      </view>

      <view class="action-row">
        <button class="mini-btn" @click="chatWith(elder.id)">聊天回访</button>
        <button class="mini-btn warm" @click="callElder(elder.id)">语音回访</button>
        <button class="mini-btn secondary" @click="sendReminder(elder.id)">发送提醒</button>
        <button class="mini-btn secondary" @click="togglePriority(elder.id)">重点标记</button>
        <button class="mini-btn danger" @click="toggleBlacklist(elder.id)">黑名单</button>
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
import type { RiskLevel } from '@/types/app'

const store = useAppStore()
const elders = computed(() => store.guardianElders)

const levelTextMap: Record<RiskLevel, string> = {
  high: '高风险',
  medium: '中风险',
  low: '稳定',
}

function chatWith(elderId: string) {
  store.selectElder(elderId)
  openPage('/pages/guardian/chat')
}

function sendReminder(elderId: string) {
  store.selectElder(elderId)
  store.sendRemoteReminder('陌生电话和链接先别处理，先发消息给我。')
  uni.showToast({
    title: '提醒已发送',
    icon: 'success',
  })
}

function callElder(elderId: string) {
  store.selectElder(elderId)
  store.startCall(elderId, 'guardian', 'outgoing')
  openPage('/pages/guardian/call')
}

function isPriority(elderId: string) {
  return Boolean(store.contacts.find((item) => item.id === elderId)?.isPriority)
}

function isBlacklisted(elderId: string) {
  return Boolean(store.contacts.find((item) => item.id === elderId)?.isBlacklisted)
}

function togglePriority(elderId: string) {
  store.togglePriorityContact(elderId)
  uni.showToast({
    title: '已更新重点标记',
    icon: 'success',
  })
}

function toggleBlacklist(elderId: string) {
  store.toggleBlacklistContact(elderId)
  uni.showToast({
    title: '已更新黑名单',
    icon: 'success',
  })
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
.elder-row {
  display: flex;
  gap: 18rpx;
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
.elder-main {
  flex: 1;
}
.name-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}
.name {
  font-size: 31rpx;
  font-weight: 700;
}
.risk-tag {
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  font-size: 20rpx;
}
.risk-tag.high {
  background: #fee2e2;
  color: #991b1b;
}
.risk-tag.medium {
  background: #fff0d2;
  color: #8a5a00;
}
.risk-tag.low {
  background: #dcfce7;
  color: #166534;
}
.meta,
.summary {
  display: block;
  margin-top: 8rpx;
  font-size: 25rpx;
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.metrics-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 18rpx;
}
.metric {
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #f3f7f8;
  font-size: 22rpx;
  color: var(--ss-color-subtext);
}
.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
  margin-top: 20rpx;
}
.mini-btn {
  flex: 1 1 calc(50% - 14rpx);
  border: none;
  border-radius: 18rpx;
  background: var(--ss-color-primary);
  color: #fff;
  font-size: 26rpx;
}
.mini-btn.secondary {
  background: #eef2f7;
  color: var(--ss-color-text);
}
.mini-btn.warm {
  background: #fff0d2;
  color: #8a5a00;
}
.mini-btn.danger {
  background: #fee2e2;
  color: #991b1b;
}
</style>
