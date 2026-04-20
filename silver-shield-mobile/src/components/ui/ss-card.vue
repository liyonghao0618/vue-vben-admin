<template>
  <view class="ss-card">
    <slot />
  </view>
</template>

<style scoped lang="scss">
.ss-card {
  background: var(--ss-color-surface);
  border: 2rpx solid var(--ss-color-border);
  border-radius: var(--ss-card-radius);
  box-shadow: var(--ss-shadow-soft);
  padding: 28rpx;
}
</style>
