<template>
  <view class="page-shell">
    <ss-topbar title="通话记录" subtitle="查看最近与家人、社区的语音通话结果。" show-back />

    <ss-card>
      <ss-section-title title="通话方案预留" subtitle="当前以本地状态机演示，后续替换为真实 RTC 接入。" />
      <text class="plan">{{ store.callSdkPlan }}</text>
    </ss-card>

    <ss-feedback-state
      v-if="!records.length"
      empty
      empty-title="还没有通话记录"
      empty-description="从联系人页、风险详情或求助详情发起语音通话后，这里会自动沉淀记录。"
    />

    <ss-card v-for="record in records" :key="record.id">
      <view class="record-card">
        <text class="name">{{ record.contactName }}</text>
        <text class="meta">{{ directionLabel(record.direction) }} · {{ statusLabel(record.status) }}</text>
        <text class="meta">{{ record.startedAt }} · 时长 {{ record.durationLabel }}</text>
        <text class="summary">{{ record.summaryText || '待补充通话摘要。' }}</text>
        <text class="summary-tag">{{ record.summaryStatus === 'uploaded' ? '摘要已上传预留' : '待上传摘要' }}</text>
      </view>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import { useAppStore } from '@/store/app'
import type { CallDirection, CallStatus } from '@/types/app'

const store = useAppStore()
const records = computed(() => store.elderCallRecords)

function directionLabel(direction: CallDirection) {
  return direction === 'incoming' ? '呼入' : '呼出'
}

function statusLabel(status: CallStatus) {
  const map: Record<string, string> = {
    ended: '已完成',
    failed: '异常中断',
    missed: '未接通',
    rejected: '已拒接',
  }

  return map[status] || status
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  background: #f6f8f2;
}
.plan,
.meta,
.summary {
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
.summary-tag {
  width: fit-content;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: #eef2f7;
  font-size: var(--ss-font-size-caption);
  color: var(--ss-color-text);
}
</style>
