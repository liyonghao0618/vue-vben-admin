<template>
  <view class="page-shell">
    <ss-topbar title="风险通知" subtitle="优先处理高风险，再逐条完成回访和提醒。" show-back />
    <ss-feedback-state
      v-if="store.isWeakNetwork"
      weak-network
      weak-title="弱网下风险通知可能延迟"
      weak-description="建议优先处理已有高风险，再在网络恢复后刷新。"
      :hint="networkHint"
      @retry="refreshRisks"
    />
    <ss-feedback-state
      v-else-if="isLoading"
      loading
      loading-title="正在刷新风险列表"
      loading-description="正在重新拉取聊天和链接的识别结果。"
    />
    <ss-feedback-state
      v-else-if="hasError"
      error
      error-title="风险通知刷新失败"
      error-description="当前无法完成风险列表刷新，请稍后重试。"
      @retry="refreshRisks"
    />
    <ss-feedback-state
      v-else-if="!risks.length"
      empty
      empty-title="当前没有风险通知"
      empty-description="新的聊天识别、链接识别或通话分析结果会展示在这里。"
    />

    <ss-card v-for="risk in risks" :key="risk.id">
      <view class="risk-head">
        <text class="risk-badge" :class="risk.level">{{ risk.level.toUpperCase() }}</text>
        <text class="risk-time">{{ risk.time }}</text>
      </view>
      <text class="risk-title">{{ risk.title }}</text>
      <text class="risk-summary">{{ risk.summary }}</text>
      <view class="risk-meta-row">
        <text class="risk-meta">来源：{{ sourceLabelMap[risk.source || 'manual'] }}</text>
        <text class="risk-meta">建议：优先回访老人</text>
      </view>
      <view class="action-row">
        <button class="mini-btn" @click="openRisk(risk.id)">查看详情</button>
        <button class="mini-btn secondary" @click="goRiskChat(risk.id)">去聊天确认</button>
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
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
const risks = computed(() => store.guardianRiskRecords)
const isLoading = ref(true)
const hasError = ref(false)
const networkHint = computed(() => `网络类型：${store.networkType || '未知'}，上次风险刷新：${store.lastRiskRefreshAt || '尚未刷新'}`)

const sourceLabelMap: Record<string, string> = {
  chat: '聊天消息',
  link: '链接识别',
  call: '通话分析',
  manual: '人工补录',
}

onShow(() => {
  void refreshRisks()
})

async function refreshRisks() {
  isLoading.value = true
  hasError.value = false

  try {
    for (const elder of store.guardianElders) {
      await store.refreshRiskSignals(elder.id)
    }
  } catch {
    hasError.value = true
  } finally {
    isLoading.value = false
  }
}

function openRisk(riskId: string) {
  store.selectRisk(riskId)
  openPage('/pages/guardian/risk-detail')
}

function goRiskChat(riskId: string) {
  store.selectRisk(riskId)
  store.selectElder('elder-001')
  openPage('/pages/guardian/chat')
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  background: #f7f1ef;
}
.risk-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14rpx;
}
.risk-badge {
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
.risk-time,
.risk-meta {
  font-size: 23rpx;
  color: var(--ss-color-subtext);
}
.risk-title {
  display: block;
  margin-top: 16rpx;
  font-size: 32rpx;
  font-weight: 700;
}
.risk-summary {
  display: block;
  margin-top: 12rpx;
  font-size: 27rpx;
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.risk-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx 18rpx;
  margin-top: 16rpx;
}
.action-row {
  display: flex;
  gap: 14rpx;
  margin-top: 20rpx;
}
.mini-btn {
  flex: 1;
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
</style>
