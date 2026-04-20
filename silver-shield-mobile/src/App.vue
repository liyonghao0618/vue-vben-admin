<script setup lang="ts">
import { computed, watch } from 'vue'
import { onLaunch, onShow } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'

const store = useAppStore()

const elderThemeState = computed(() => ({
  fontScale: store.elderSettings.fontScale,
  contrastMode: store.elderSettings.contrastMode,
  simplifyMode: store.elderSettings.simplifyMode,
}))

function applyElderTheme() {
  if (typeof document === 'undefined') {
    return
  }

  const root = document.documentElement
  const { fontScale, contrastMode, simplifyMode } = elderThemeState.value
  const scale = fontScale === 'x-large' ? '1.18' : '1.08'

  root.style.setProperty('--ss-font-scale', scale)
  root.dataset.ssContrast = String(contrastMode)
  root.dataset.ssSimplify = String(simplifyMode)
}

onLaunch(() => {
  console.log('Silver Shield Mobile Launch')
  store.initNetworkStatus()
  applyElderTheme()
})

onShow(() => {
  console.log('Silver Shield Mobile Visible')
  applyElderTheme()
})

watch(elderThemeState, () => {
  applyElderTheme()
}, { deep: true, immediate: true })
</script>

<style lang="scss">
page {
  background: var(--ss-color-bg);
  color: var(--ss-color-text);
  font-family: 'Avenir Next', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
  font-size: calc(28rpx * var(--ss-font-scale, 1));
}
</style>
