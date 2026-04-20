<template>
  <view class="page-shell">
    <ss-topbar title="求助详情" subtitle="优先电话回访老人，再同步社区或主业务系统。" show-back />

    <ss-card v-if="sosAlert">
      <view class="hero-block">
        <text class="status-tag" :class="sosAlert.status">{{ statusText }}</text>
        <text class="hero-title">{{ sosAlert.elderName }} 的求助工单</text>
        <text class="hero-text">{{ sosAlert.summary }}</text>
        <text class="hero-meta">{{ sosAlert.time }} · 工单号 {{ sosAlert.linkedTicketNo || '待生成' }}</text>
      </view>
    </ss-card>

    <ss-card v-if="sosAlert">
      <ss-section-title title="求助详情" />
      <text class="block-text">{{ sosAlert.detail }}</text>
      <text class="block-text">联系人：{{ sosAlert.reporterPhone || '未同步' }}</text>
      <text class="block-text">位置：{{ sosAlert.location || '待确认' }}</text>
    </ss-card>

    <ss-card v-if="sosAlert">
      <ss-section-title title="联动进度" />
      <text class="block-text">{{ sosAlert.latestAction || '等待系统同步最新动作。' }}</text>
      <text v-if="store.mainServiceNotice" class="block-meta">{{ store.mainServiceNotice }}</text>
    </ss-card>

    <view v-if="sosAlert" class="action-group">
      <button class="cta-button" @click="goChat">立即回访老人</button>
      <button class="cta-button warm" @click="startCall">立即拨打语音</button>
      <button
        v-if="sosAlert.status === 'pending'"
        class="cta-button secondary"
        @click="markProcessing"
      >
        标记处理中
      </button>
      <button
        v-if="sosAlert.status !== 'resolved'"
        class="cta-button muted"
        @click="resolveAlert"
      >
        记录处理完成
      </button>
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

const sosAlert = computed(() => store.selectedSosAlert)
const statusText = computed(() => {
  if (!sosAlert.value) {
    return '待处理'
  }

  if (sosAlert.value.status === 'resolved') {
    return '已完成'
  }

  if (sosAlert.value.status === 'processing') {
    return '处理中'
  }

  return '待处理'
})

function goChat() {
  if (!sosAlert.value) {
    return
  }

  store.selectElder(sosAlert.value.elderId)
  openPage('/pages/guardian/chat')
}

function startCall() {
  if (!sosAlert.value) {
    return
  }

  store.selectElder(sosAlert.value.elderId)
  store.startCall(sosAlert.value.elderId, 'guardian', 'outgoing')
  openPage('/pages/guardian/call')
}

function markProcessing() {
  if (!sosAlert.value) {
    return
  }

  store.markSosHandled(sosAlert.value.id)
  uni.showToast({
    title: '已标记处理中',
    icon: 'success',
  })
}

function resolveAlert() {
  if (!sosAlert.value) {
    return
  }

  store.resolveSosAlert(sosAlert.value.id)
  uni.showToast({
    title: '已记录完成',
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
  background: linear-gradient(180deg, #fff7f5 0%, #eef4f6 100%);
}
.hero-block {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}
.status-tag {
  width: fit-content;
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
}
.status-tag.pending {
  background: #fee2e2;
  color: #991b1b;
}
.status-tag.processing {
  background: #fff0d2;
  color: #8a5a00;
}
.status-tag.resolved {
  background: #dcfce7;
  color: #166534;
}
.hero-title {
  font-size: 36rpx;
  font-weight: 700;
}
.hero-text,
.hero-meta,
.block-text,
.block-meta {
  font-size: 27rpx;
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.block-meta {
  margin-top: 12rpx;
  color: #0f766e;
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
  background: #fff0d2;
  color: #8a5a00;
}
.cta-button.warm {
  background: #dff7f2;
  color: var(--ss-color-primary);
}
.cta-button.muted {
  background: #eef2f7;
  color: var(--ss-color-text);
}
</style>
