<template>
  <view class="topbar">
    <view>
      <text class="title">{{ title }}</text>
      <text v-if="subtitle" class="subtitle">{{ subtitle }}</text>
    </view>
    <button v-if="showBack" class="back-button" @click="goBack">返回</button>
  </view>
</template>

<script setup lang="ts">
import { backPage } from '@/utils/navigation'

withDefaults(defineProps<{
  title: string
  subtitle?: string
  showBack?: boolean
}>(), {
  showBack: false,
})

function goBack() {
  backPage()
}
</script>

<style scoped lang="scss">
.topbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
}

.title {
  display: block;
  font-size: var(--ss-font-size-title);
  font-weight: 700;
}

.subtitle {
  display: block;
  margin-top: 10rpx;
  font-size: var(--ss-font-size-caption);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}

.back-button {
  min-width: 120rpx;
  border: none;
  border-radius: 18rpx;
  background: #eef5f3;
  color: var(--ss-color-primary);
  font-size: var(--ss-font-size-caption);
}
</style>
