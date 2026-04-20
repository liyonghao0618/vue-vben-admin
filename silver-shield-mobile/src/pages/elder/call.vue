<template>
  <view class="page-shell">
    <ss-topbar title="语音通话" subtitle="App 内语音通话演示流程，后续可替换真实 SDK。" show-back />

    <ss-card v-if="call">
      <view class="hero-card">
        <view class="avatar">{{ call.avatarText }}</view>
        <text class="name">{{ call.contactName }}</text>
        <text class="relation">{{ call.relation }}</text>
        <text class="status">{{ statusText }}</text>
        <text class="timer">{{ timerText }}</text>
        <text class="plan">{{ call.sdkPlan }}</text>
      </view>
    </ss-card>

    <ss-card v-if="call">
      <ss-section-title title="通话控制" subtitle="覆盖拨打、接听、通话中、挂断和异常处理。" />
      <view class="action-grid">
        <button v-if="call.status === 'ringing'" class="action-button warm" @click="acceptCall">接听</button>
        <button v-if="call.status === 'ringing' || call.status === 'connecting'" class="action-button" @click="connectCall">模拟接通</button>
        <button v-if="call.status === 'connected'" class="action-button" @click="tickCall">增加 30 秒</button>
        <button class="action-button danger" @click="endCall">挂断</button>
        <button class="action-button secondary" @click="failCall">网络异常</button>
        <button v-if="call.status === 'ringing'" class="action-button secondary" @click="rejectCall">拒接</button>
      </view>
    </ss-card>

    <ss-card v-if="call">
      <ss-section-title title="摘要上传预留" subtitle="真实接入后可上传 ASR 结果、风险标签与回访结论。" />
      <textarea v-model="summaryDraft" class="summary-input" maxlength="120" />
      <button class="save-button" @click="saveAndFinish">保存摘要并结束</button>
    </ss-card>

    <ss-card v-else>
      <text class="empty-text">当前没有进行中的通话，您可以从联系人、风险详情、求助详情或老人列表发起。</text>
      <button class="save-button secondary" @click="openPage('/pages/elder/call-records')">查看通话记录</button>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
const call = computed(() => store.activeCallSession)
const summaryDraft = ref('')

watch(call, (value) => {
  summaryDraft.value = value?.summaryDraft || ''
}, { immediate: true })

const timerText = computed(() => {
  if (!call.value) {
    return '--:--'
  }

  const mins = Math.floor(call.value.durationSeconds / 60)
  const secs = call.value.durationSeconds % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

const statusText = computed(() => {
  if (!call.value) {
    return '无通话'
  }

  const map: Record<string, string> = {
    ringing: call.value.direction === 'incoming' ? '来电响铃中' : '正在呼叫对方',
    connecting: '正在建立语音通道',
    connected: '通话进行中',
    ended: '通话已结束',
    failed: '通话异常',
    missed: '未接通',
    rejected: '已拒接',
  }

  return map[call.value.status] || '通话处理中'
})

function acceptCall() {
  store.acceptCurrentCall()
}

function connectCall() {
  store.connectCurrentCall()
}

function tickCall() {
  store.tickCurrentCall(30)
}

function endCall() {
  persistSummary()
  store.endCurrentCall('ended')
  openPage('/pages/elder/call-records')
}

function failCall() {
  persistSummary()
  store.endCurrentCall('failed', '网络波动，语音通道已断开。')
  openPage('/pages/elder/call-records')
}

function rejectCall() {
  persistSummary()
  store.endCurrentCall('rejected')
  openPage('/pages/elder/call-records')
}

function saveAndFinish() {
  endCall()
}

function persistSummary() {
  if (!store.activeCallSession) {
    return
  }

  store.activeCallSession.summaryDraft = summaryDraft.value.trim() || store.activeCallSession.summaryDraft
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  background: linear-gradient(180deg, #f6f9fb 0%, #eef3ea 100%);
}
.hero-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 14rpx;
}
.avatar {
  width: 132rpx;
  height: 132rpx;
  border-radius: 50%;
  background: #dff7f2;
  color: var(--ss-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  font-weight: 700;
}
.name {
  font-size: var(--ss-font-size-title);
  font-weight: 700;
}
.relation,
.status,
.plan,
.empty-text {
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.timer {
  font-size: calc(var(--ss-font-size-hero) * 0.9);
  font-weight: 700;
  color: var(--ss-color-text);
}
.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
  margin-top: 18rpx;
}
.action-button,
.save-button {
  border: none;
  border-radius: 22rpx;
  font-size: var(--ss-font-size-body);
  font-weight: 700;
}
.action-button {
  background: #dff7f2;
  color: var(--ss-color-primary);
}
.action-button.warm {
  background: #fff0d2;
  color: #8a5a00;
}
.action-button.danger {
  background: #fee2e2;
  color: #991b1b;
}
.action-button.secondary,
.save-button.secondary {
  background: #eef2f7;
  color: var(--ss-color-text);
}
.summary-input {
  width: 100%;
  min-height: 180rpx;
  margin-top: 16rpx;
  padding: 20rpx;
  border-radius: 22rpx;
  background: #f7faf7;
  font-size: var(--ss-font-size-body);
}
.save-button {
  margin-top: 16rpx;
  background: var(--ss-color-primary);
  color: #fff;
}
</style>
