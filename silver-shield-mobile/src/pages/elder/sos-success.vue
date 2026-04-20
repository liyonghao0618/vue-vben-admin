<template>
  <view class="page-shell">
    <ss-card>
      <view class="result-box">
        <text class="result-title">求助已发送</text>
        <text class="result-desc">系统已经通知李女士和社区协助联系人，请保持电话畅通，不要继续和可疑对象交流。</text>
        <text class="result-meta">本次累计求助次数：{{ store.sosCount }}</text>
        <text v-if="latestSos?.linkedTicketNo" class="result-meta">主业务系统工单：{{ latestSos.linkedTicketNo }}</text>
        <text v-if="latestSos?.latestAction" class="result-meta">{{ latestSos.latestAction }}</text>
        <text v-if="store.mainServiceNotice" class="result-note">{{ store.mainServiceNotice }}</text>
      </view>
      <view class="action-group">
        <button class="primary-btn" @click="openPage('/pages/elder/chat')">立即给家属发消息</button>
        <button class="secondary-btn" @click="openPage('/pages/elder/home')">返回首页</button>
      </view>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import SsCard from '@/components/ui/ss-card.vue'
import { computed } from 'vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
const latestSos = computed(() => store.selectedSosAlert || store.activeSosAlerts[0])
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 40rpx 24rpx;
  background: linear-gradient(180deg, #fff7f5 0%, #f7f0e6 100%);
}
.result-box {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.result-title {
  font-size: 44rpx;
  font-weight: 700;
  color: #991b1b;
}
.result-desc,
.result-meta {
  font-size: 28rpx;
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.result-note {
  font-size: 24rpx;
  line-height: 1.6;
  color: #0f766e;
}
.action-group {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-top: 28rpx;
}
.primary-btn,
.secondary-btn {
  border: none;
  border-radius: 20rpx;
  font-size: 30rpx;
}
.primary-btn {
  background: var(--ss-color-danger);
  color: #fff;
}
.secondary-btn {
  background: #eef2f7;
  color: var(--ss-color-text);
}
</style>
