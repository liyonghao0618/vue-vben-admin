<template>
  <view class="page-shell">
    <ss-topbar title="风险详情" subtitle="先帮老人停下可疑操作，再完成回访和远程提醒。" show-back />

    <ss-card v-if="risk">
      <view class="hero-alert">
        <text class="risk-badge" :class="risk.level">{{ risk.level.toUpperCase() }}</text>
        <text class="risk-title">{{ risk.title }}</text>
        <text class="risk-summary">{{ risk.summary }}</text>
        <text class="risk-meta">{{ risk.time }} · 来源：{{ sourceLabelMap[risk.source || 'manual'] }}</text>
      </view>
    </ss-card>

    <ss-card v-if="risk">
      <ss-section-title title="为什么危险" />
      <text class="block-text">{{ risk.reason }}</text>
      <text v-if="risk.matchedText?.length" class="block-meta">命中词：{{ risk.matchedText.join('、') }}</text>
    </ss-card>

    <ss-card v-if="risk">
      <ss-section-title title="建议怎么做" />
      <text class="block-text">{{ risk.suggestion }}</text>
      <text v-if="risk.confidence !== undefined" class="block-meta">风险置信度：{{ Math.round(risk.confidence * 100) }}%</text>
      <text v-if="risk.detectionStatus === 'fallback'" class="block-meta warn-text">当前为兜底识别结果，建议优先人工回访。</text>
      <text v-if="risk.followUpStatus" class="block-meta">跟进状态：{{ followUpStatusLabelMap[risk.followUpStatus] }}</text>
    </ss-card>

    <ss-card v-if="elder">
      <ss-section-title title="关联老人" />
      <text class="block-text">{{ elder.name }} · {{ elder.relation }} · 最近联系 {{ elder.lastContactAt }}</text>
      <text class="block-text">{{ elder.statusSummary }}</text>
      <text class="block-meta">今日风险 {{ elder.riskCountToday }} 条 · 待处理 {{ elder.pendingAlerts }} 条</text>
    </ss-card>

    <ss-card v-if="store.communityContacts.length">
      <ss-section-title title="社区协同入口" />
      <text class="block-text">如老人持续失联、情绪激动或仍在与可疑对象接触，可同步社区联系人跟进。</text>
      <text class="block-meta">可用联系人：{{ store.communityContacts.map((item) => item.name).join('、') }}</text>
    </ss-card>

    <ss-card v-if="store.aiServiceNotice">
      <ss-section-title title="识别服务提示" />
      <text class="block-text">{{ store.aiServiceNotice }}</text>
    </ss-card>

    <view class="action-group">
      <button class="cta-button" @click="goChat">立即回访老人</button>
      <button class="cta-button warm" @click="startCall">立即拨打语音</button>
      <button class="cta-button secondary" @click="sendReminder">发送远程提醒</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()

const risk = computed(() => store.selectedRisk)
const elder = computed(() => {
  const relatedId = risk.value?.relatedContactId
  return store.guardianElders.find((item) => item.id === relatedId) || store.guardianElders.find((item) => item.id === 'elder-001')
})

const sourceLabelMap: Record<string, string> = {
  chat: '聊天消息',
  link: '链接识别',
  call: '通话分析',
  manual: '人工补录',
}
const followUpStatusLabelMap: Record<string, string> = {
  pending: '待跟进',
  processing: '处理中',
  resolved: '已完成',
}

function goChat() {
  store.selectElder(elder.value?.id || 'elder-001')
  openPage('/pages/guardian/chat')
}

function startCall() {
  const elderId = elder.value?.id || 'elder-001'
  store.selectElder(elderId)
  store.startCall(elderId, 'guardian', 'outgoing')
  openPage('/pages/guardian/call')
}

function sendReminder() {
  const elderId = elder.value?.id || 'elder-001'
  store.selectElder(elderId)
  store.sendRemoteReminder('这条内容有风险，先别操作，我正在帮你核验。')
  uni.showToast({
    title: '提醒已发送',
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
  background: #fbf1ee;
}
.hero-alert {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}
.risk-badge {
  width: fit-content;
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
}
.risk-badge.high {
  background: #fee2e2;
  color: #991b1b;
}
.risk-badge.medium {
  background: #fff0d2;
  color: #8a5a00;
}
.risk-badge.low {
  background: #dcfce7;
  color: #166534;
}
.risk-title {
  font-size: 36rpx;
  font-weight: 700;
}
.risk-summary,
.block-text,
.risk-meta {
  font-size: 28rpx;
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.block-meta {
  display: block;
  margin-top: 12rpx;
  font-size: 23rpx;
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.warn-text {
  color: #b45309;
}
.action-group {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}
.cta-button {
  border: none;
  border-radius: 20rpx;
  background: var(--ss-color-danger);
  color: #fff;
  font-size: 30rpx;
  font-weight: 700;
}
.cta-button.secondary {
  background: #eef2f7;
  color: var(--ss-color-text);
}
.cta-button.warm {
  background: #fff0d2;
  color: #8a5a00;
}
</style>
