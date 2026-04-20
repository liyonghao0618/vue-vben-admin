<template>
  <view class="page-shell">
    <ss-topbar title="通话记录" subtitle="查看守护人回访通话结果与摘要上传预留。" show-back />

    <ss-card>
      <ss-section-title title="通信方案" subtitle="当前完成页面与状态流，SDK 对接位已预留。" />
      <text class="plan">{{ store.callSdkPlan }}</text>
    </ss-card>

    <ss-feedback-state
      v-if="!records.length"
      empty
      empty-title="还没有通话记录"
      empty-description="发起语音回访或接听老人来电后，这里会展示通话结果和摘要状态。"
    />

    <ss-card v-for="record in records" :key="record.id">
      <view class="record-card">
        <text class="name">{{ record.contactName }}</text>
        <text class="meta">{{ directionLabel(record.direction) }} · {{ statusLabel(record.status) }}</text>
        <text class="meta">{{ record.startedAt }} · 时长 {{ record.durationLabel }}</text>
        <textarea v-model="draftMap[record.id]" class="summary-input" maxlength="160" />
        <view class="action-row">
          <text class="summary-tag">{{ record.summaryStatus === 'uploaded' ? '摘要已上传预留' : '待上传摘要' }}</text>
          <button class="save-button" @click="saveSummary(record.id)">保存摘要</button>
        </view>
        <text v-if="record.postCallRiskLevel" class="meta">通话后风险：{{ riskLevelLabel(record.postCallRiskLevel) }}</text>
        <text v-if="record.followUpAction" class="meta">{{ record.followUpAction }}</text>
      </view>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { computed, reactive, watchEffect } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import { useAppStore } from '@/store/app'
import type { CallDirection, CallStatus, RiskLevel } from '@/types/app'

const store = useAppStore()
const records = computed(() => store.guardianCallRecords)
const draftMap = reactive<Record<string, string>>({})

watchEffect(() => {
  records.value.forEach((record) => {
    if (draftMap[record.id] === undefined) {
      draftMap[record.id] = record.summaryText || ''
    }
  })
})

function directionLabel(direction: CallDirection) {
  return direction === 'incoming' ? '呼入' : '呼出'
}

function statusLabel(status: CallStatus) {
  const map: Record<string, string> = {
    ended: '已完成',
    failed: '异常中断',
    missed: '无人接听',
    rejected: '对方拒接',
  }

  return map[status] || status
}

function saveSummary(recordId: string) {
  store.updateCallSummary(recordId, draftMap[recordId] || '已预留通话摘要上传内容。')
  uni.showToast({
    title: '摘要已保存',
    icon: 'success',
  })
}

function riskLevelLabel(level: RiskLevel) {
  const map: Record<RiskLevel, string> = {
    high: '高风险',
    medium: '中风险',
    low: '低风险',
  }

  return map[level]
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
.plan,
.meta {
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.record-card {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}
.name {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
.summary-input {
  width: 100%;
  min-height: 150rpx;
  padding: 20rpx;
  border-radius: 22rpx;
  background: #f7faf7;
  font-size: var(--ss-font-size-body);
}
.action-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}
.summary-tag {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: #eef2f7;
  font-size: var(--ss-font-size-caption);
  color: var(--ss-color-text);
}
.save-button {
  border: none;
  border-radius: 18rpx;
  background: var(--ss-color-primary);
  color: #fff;
  font-size: var(--ss-font-size-body);
  font-weight: 700;
}
</style>
