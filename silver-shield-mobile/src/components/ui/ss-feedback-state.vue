<template>
  <view class="state-card" :class="modeClass">
    <text class="state-title">{{ titleText }}</text>
    <text class="state-desc">{{ descriptionText }}</text>
    <text v-if="hint" class="state-hint">{{ hint }}</text>
    <button v-if="showRetry" class="state-button" @click="$emit('retry')">{{ retryText }}</button>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    loading?: boolean
    error?: boolean
    empty?: boolean
    weakNetwork?: boolean
    loadingTitle?: string
    loadingDescription?: string
    errorTitle?: string
    errorDescription?: string
    emptyTitle?: string
    emptyDescription?: string
    weakTitle?: string
    weakDescription?: string
    hint?: string
    retryText?: string
  }>(),
  {
    retryText: '重试',
  },
)

defineEmits<{
  retry: []
}>()

const mode = computed(() => {
  if (props.loading) return 'loading'
  if (props.error) return 'error'
  if (props.empty) return 'empty'
  if (props.weakNetwork) return 'weak'
  return 'default'
})

const modeClass = computed(() => `mode-${mode.value}`)
const showRetry = computed(() => props.error || props.weakNetwork)
const titleText = computed(() => {
  const titleMap = {
    loading: props.loadingTitle || '正在准备内容',
    error: props.errorTitle || '当前加载失败',
    empty: props.emptyTitle || '暂时没有内容',
    weak: props.weakTitle || '当前网络较弱',
    default: props.emptyTitle || '暂时没有内容',
  }

  return titleMap[mode.value]
})

const descriptionText = computed(() => {
  const descriptionMap = {
    loading: props.loadingDescription || '页面正在同步最新状态，请稍等片刻。',
    error: props.errorDescription || '可以稍后再试，或点击下方按钮重新加载。',
    empty: props.emptyDescription || '新的记录出现后会自动展示在这里。',
    weak: props.weakDescription || '识别结果和通知可能延迟，建议切换到更稳定的网络后重试。',
    default: props.emptyDescription || '新的记录出现后会自动展示在这里。',
  }

  return descriptionMap[mode.value]
})
</script>

<style scoped lang="scss">
.state-card {
  padding: 32rpx 28rpx;
  border-radius: 28rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  background: #fffdf8;
  border: 2rpx dashed rgba(15, 118, 110, 0.18);
}
.state-card.mode-error {
  background: #fff5f5;
  border-color: rgba(185, 28, 28, 0.2);
}
.state-card.mode-weak {
  background: #fff8eb;
  border-color: rgba(180, 83, 9, 0.22);
}
.state-title {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
.state-desc,
.state-hint {
  font-size: var(--ss-font-size-body);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.state-hint {
  font-size: var(--ss-font-size-caption);
}
.state-button {
  margin-top: 8rpx;
  border: none;
  border-radius: 18rpx;
  background: var(--ss-color-primary);
  color: #fff;
  font-size: var(--ss-font-size-body);
}
</style>
