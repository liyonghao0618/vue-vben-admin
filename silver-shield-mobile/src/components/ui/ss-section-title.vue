<template>
  <view class="section-title-wrap">
    <text class="section-title">{{ title }}</text>
    <text v-if="subtitle" class="section-subtitle">{{ subtitle }}</text>
  </view>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<style scoped lang="scss">
.section-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.section-title {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
  color: var(--ss-color-text);
}

.section-subtitle {
  font-size: var(--ss-font-size-caption);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
</style>
