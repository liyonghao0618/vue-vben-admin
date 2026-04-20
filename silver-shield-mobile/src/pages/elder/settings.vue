<template>
  <view class="page-shell">
    <ss-topbar title="适老化设置" subtitle="让页面更大、更清楚、更少干扰。" show-back />

    <ss-card>
      <ss-section-title title="字体大小" />
      <view class="option-row">
        <button class="option-btn" :class="{ active: settings.fontScale === 'large' }" @click="setFontScale('large')">大号</button>
        <button class="option-btn" :class="{ active: settings.fontScale === 'x-large' }" @click="setFontScale('x-large')">超大号</button>
      </view>
    </ss-card>

    <ss-card>
      <ss-section-title title="高对比显示" subtitle="重要信息更醒目。" />
      <switch :checked="settings.contrastMode" color="#0f766e" @change="toggleContrast" />
    </ss-card>

    <ss-card>
      <ss-section-title title="核心操作少一步" subtitle="首页直接看到最常用入口，减少跳转层级。" />
      <switch :checked="settings.simplifyMode" color="#0f766e" @change="toggleSimplifyMode" />
    </ss-card>

    <ss-card>
      <ss-section-title title="语音播报预留" subtitle="后续可接入重点风险内容播报。" />
      <switch :checked="settings.voiceBroadcastReserved" color="#0f766e" @change="toggleVoiceReserved" />
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import { useAppStore } from '@/store/app'
import type { ElderSettings } from '@/types/app'

const store = useAppStore()
const settings = computed(() => store.elderSettings)

function setFontScale(fontScale: ElderSettings['fontScale']) {
  store.updateElderSettings({ fontScale })
}

function toggleContrast(event: Event) {
  store.updateElderSettings({ contrastMode: getSwitchValue(event) })
}

function toggleVoiceReserved(event: Event) {
  store.updateElderSettings({ voiceBroadcastReserved: getSwitchValue(event) })
}

function toggleSimplifyMode(event: Event) {
  store.updateElderSettings({ simplifyMode: getSwitchValue(event) })
}

function getSwitchValue(event: Event) {
  const detail = event as Event & { detail?: { value?: boolean } }
  const target = event.target as HTMLInputElement | null

  return typeof detail.detail?.value === 'boolean'
    ? detail.detail.value
    : Boolean(target?.checked)
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  background: #f5f3eb;
}
.option-row {
  display: flex;
  gap: 14rpx;
  margin-top: 18rpx;
}
.option-btn {
  flex: 1;
  border: none;
  border-radius: 18rpx;
  background: #eef2f7;
  color: var(--ss-color-text);
  font-size: var(--ss-font-size-body);
}
.option-btn.active {
  background: var(--ss-color-primary);
  color: #fff;
}
</style>
