<template>
  <view class="page-shell">
    <view class="hero">
      <text class="eyebrow">Silver Shield Login</text>
      <text class="title">登录并进入对应角色首页</text>
      <text class="subtitle">先用 mock 登录态完成 H5 演示，后续再替换为真实接口。</text>
    </view>

    <ss-card>
      <ss-section-title title="选择角色" subtitle="不同角色会进入不同首页，并加载不同资料。" />
      <view class="role-switch">
        <button
          v-for="role in roles"
          :key="role.value"
          class="role-chip"
          :class="{ active: form.role === role.value }"
          @click="form.role = role.value"
        >
          {{ role.label }}
        </button>
      </view>

      <view class="form-list">
        <view class="form-item">
          <text class="label">账号</text>
          <input v-model="form.account" class="input" placeholder="输入演示账号，例如 elder-demo" />
        </view>
        <view class="form-item">
          <text class="label">密码</text>
          <input v-model="form.password" class="input" password placeholder="输入任意密码即可登录" />
        </view>
      </view>

      <text v-if="store.loginError" class="error-text">{{ store.loginError }}</text>

      <button class="submit-button" @click="submitLogin">登录并进入首页</button>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import { useAppStore } from '@/store/app'
import { navigateToRoleHome } from '@/utils/navigation'
import type { LoginForm, UserRole } from '@/types/app'

const store = useAppStore()

const roles: Array<{ label: string; value: UserRole }> = [
  { label: '老年用户端', value: 'elder' },
  { label: '子女 / 守护人端', value: 'guardian' },
]

const form = reactive<LoginForm>({
  account: 'elder-demo',
  password: '123456',
  role: 'elder',
})

async function submitLogin() {
  const success = await store.login(form)
  if (!success) {
    return
  }

  navigateToRoleHome(form.role, true)
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 40rpx 28rpx 48rpx;
  background:
    radial-gradient(circle at top left, rgba(15, 118, 110, 0.16), transparent 30%),
    linear-gradient(180deg, #f9f6ee 0%, #eef3ef 100%);
  display: flex;
  flex-direction: column;
  gap: 28rpx;
}
.hero {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.eyebrow {
  font-size: 24rpx;
  letter-spacing: 4rpx;
  color: var(--ss-color-primary);
}
.title {
  font-size: 52rpx;
  font-weight: 700;
  line-height: 1.3;
}
.subtitle {
  font-size: 28rpx;
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.role-switch {
  display: flex;
  gap: 16rpx;
  margin-top: 20rpx;
}
.role-chip {
  flex: 1;
  border: none;
  border-radius: 20rpx;
  background: #edf5f3;
  color: var(--ss-color-primary);
  font-size: 26rpx;
}
.role-chip.active {
  background: var(--ss-color-primary);
  color: #fff;
}
.form-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-top: 24rpx;
}
.form-item {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}
.label {
  font-size: 26rpx;
  font-weight: 600;
}
.input {
  height: 92rpx;
  border-radius: 18rpx;
  background: #f7f7f3;
  padding: 0 24rpx;
  font-size: 28rpx;
}
.error-text {
  display: block;
  margin-top: 18rpx;
  color: var(--ss-color-danger);
  font-size: 24rpx;
}
.submit-button {
  margin-top: 24rpx;
  border: none;
  border-radius: 20rpx;
  background: var(--ss-color-primary);
  color: #fff;
  font-size: 30rpx;
  font-weight: 700;
}
</style>
