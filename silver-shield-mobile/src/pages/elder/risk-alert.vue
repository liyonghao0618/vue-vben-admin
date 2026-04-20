<template>
  <view class="page-shell">
    <ss-topbar title="风险提醒" subtitle="看到以下内容时，不要转账，不要点链接。" show-back />

    <ss-card v-if="topRisk">
      <view class="hero-alert">
        <text class="risk-badge">{{ topRisk.level.toUpperCase() }}</text>
        <text class="risk-title">{{ topRisk.title }}</text>
        <text class="risk-summary">{{ topRisk.summary }}</text>
        <view class="strong-warning">
          <text class="warning-title">现在先做这 3 件事</text>
          <text class="warning-step">1. 不转账</text>
          <text class="warning-step">2. 不点陌生链接</text>
          <text class="warning-step">3. 立即联系家属确认</text>
        </view>
      </view>
    </ss-card>

    <ss-voice-bar
      :enabled="store.elderSettings.voiceBroadcastReserved"
      :text="topRisk ? `${topRisk.title}。${topRisk.summary}` : '风险提醒页已预留语音播报能力。'"
    />

    <ss-card v-if="topRisk">
      <ss-section-title title="为什么危险" />
      <text class="block-text">{{ topRisk.reason }}</text>
      <text v-if="topRisk.matchedText?.length" class="block-meta">命中词：{{ topRisk.matchedText.join('、') }}</text>
    </ss-card>

    <ss-card v-if="topRisk">
      <ss-section-title title="建议怎么做" />
      <text class="block-text">{{ topRisk.suggestion }}</text>
      <text v-if="topRisk.confidence !== undefined" class="block-meta">风险置信度：{{ Math.round(topRisk.confidence * 100) }}%</text>
      <text v-if="topRisk.detectionStatus === 'fallback'" class="block-meta warn-text">当前为兜底提示，请优先人工核验。</text>
    </ss-card>

    <ss-card v-if="store.aiServiceNotice">
      <ss-section-title title="识别服务提示" />
      <text class="block-text">{{ store.aiServiceNotice }}</text>
    </ss-card>

    <ss-feedback-state
      v-if="!topRisk"
      empty
      empty-title="当前没有新的风险提醒"
      empty-description="当聊天、链接或后续通话分析命中风险后，这里会展示详细原因和建议。"
    />

    <button class="cta-button" @click="goChat">先联系家属确认</button>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import SsVoiceBar from '@/components/ui/ss-voice-bar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
const topRisk = computed(() => store.latestHighRisk)

function goChat() {
  store.selectContact('guardian-li')
  openPage('/pages/elder/chat')
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
  padding: 8rpx;
}
.risk-badge {
  width: fit-content;
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  background: #fee2e2;
  color: #991b1b;
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}
.risk-title {
  font-size: var(--ss-font-size-title);
  font-weight: 700;
}
.risk-summary,
.block-text {
  font-size: var(--ss-font-size-body);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.strong-warning {
  margin-top: 8rpx;
  padding: 22rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
  color: #fff;
  box-shadow: var(--ss-shadow-strong);
}
.warning-title {
  display: block;
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
.warning-step {
  display: block;
  margin-top: 10rpx;
  font-size: var(--ss-font-size-body);
}
.block-meta {
  display: block;
  margin-top: 12rpx;
  font-size: var(--ss-font-size-caption);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.warn-text {
  color: #b45309;
}
.cta-button {
  margin-top: 12rpx;
  border: none;
  border-radius: 20rpx;
  background: var(--ss-color-danger);
  color: #fff;
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
</style>
