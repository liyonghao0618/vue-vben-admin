<template>
  <view class="page-shell">
    <ss-topbar title="您好，{{ displayName }}" :subtitle="welcomeText" />

    <ss-card>
      <view class="alert-banner" :class="{ danger: hasHighRisk }" @click="openPage('/pages/elder/risk-alert')">
        <view class="banner-main">
          <text class="banner-tag">{{ hasHighRisk ? '高风险强提醒' : '安全提醒' }}</text>
          <text class="banner-title">{{ topRisk?.title || '当前没有新的高风险提醒' }}</text>
          <text class="banner-desc">{{ topRisk?.summary || '遇到转账、验证码、链接时，先停一停，再联系家人确认。' }}</text>
        </view>
        <view class="banner-side">
          <text class="banner-action">{{ hasHighRisk ? '立即查看' : '去查看' }}</text>
          <text v-if="hasHighRisk" class="banner-pulse">请先别操作</text>
        </view>
      </view>
    </ss-card>

    <ss-voice-bar :enabled="store.elderSettings.voiceBroadcastReserved" :text="voiceSummary" />

    <ss-card>
      <ss-section-title title="首页大按钮" subtitle="常用事情直接点，减少找入口的时间。" />
      <view class="action-grid">
        <button class="action-button action-primary" @click="chatWithGuardian">联系女儿确认</button>
        <button class="action-button" @click="callGuardian">给女儿打电话</button>
        <button class="action-button action-warm" @click="openPage('/pages/elder/contacts')">查看联系人</button>
        <button v-if="!store.elderSettings.simplifyMode" class="action-button" @click="openPage('/pages/elder/conversations')">进入聊天会话</button>
        <button class="action-button action-danger" @click="submitSos">一键求助</button>
        <button class="action-button action-muted" @click="openPage('/pages/elder/settings')">适老化设置</button>
      </view>
    </ss-card>

    <ss-card>
      <ss-section-title title="今日守护摘要" />
      <view class="summary-list">
        <view class="summary-item">
          <text class="summary-num">{{ contactsCount }}</text>
          <text class="summary-label">可联系家人 / 社区</text>
        </view>
        <view class="summary-item">
          <text class="summary-num">{{ riskCount }}</text>
          <text class="summary-label">待留意风险提醒</text>
        </view>
        <view class="summary-item">
          <text class="summary-num">{{ sosCount }}</text>
          <text class="summary-label">已发起求助次数</text>
        </view>
      </view>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import SsVoiceBar from '@/components/ui/ss-voice-bar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
void store.loadUserProfile()
store.setRole('elder')

const displayName = computed(() => store.elderName)
const welcomeText = computed(() => store.profile?.welcomeText || '重要事情先问家人，遇到风险先暂停。')
const topRisk = computed(() => store.latestHighRisk)
const hasHighRisk = computed(() => topRisk.value?.level === 'high')
const contactsCount = computed(() => store.contacts.length)
const riskCount = computed(() => store.riskRecords.length)
const sosCount = computed(() => store.sosCount)
const voiceSummary = computed(() => topRisk.value?.summary || '首页已预留语音播报位，可用于播报风险提醒和关键操作说明。')

async function submitSos() {
  await store.submitSos()
  openPage('/pages/elder/sos-success')
}

function chatWithGuardian() {
  store.selectContact('guardian-li')
  openPage('/pages/elder/chat')
}

function callGuardian() {
  store.selectContact('guardian-li')
  store.startCall('guardian-li', 'elder', 'outgoing')
  openPage('/pages/elder/call')
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  background: linear-gradient(180deg, #fffaf0 0%, #f4efe2 100%);
}
.alert-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  padding: 12rpx 6rpx;
  border-radius: 24rpx;
}
.alert-banner.danger {
  padding: 22rpx;
  background: linear-gradient(135deg, #fff4e8 0%, #ffe4e6 100%);
  border: 3rpx solid rgba(185, 28, 28, 0.2);
  box-shadow: var(--ss-shadow-strong);
}
.banner-main {
  flex: 1;
}
.banner-side {
  min-width: 160rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10rpx;
}
.banner-tag {
  display: inline-block;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: #fee2e2;
  color: var(--ss-color-danger);
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}
.banner-title {
  display: block;
  margin-top: 14rpx;
  font-size: var(--ss-font-size-title);
  font-weight: 700;
}
.banner-desc {
  display: block;
  margin-top: 10rpx;
  font-size: var(--ss-font-size-body);
  line-height: 1.7;
  color: var(--ss-color-subtext);
}
.banner-action,
.banner-pulse {
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}
.banner-action {
  color: var(--ss-color-primary);
}
.banner-pulse {
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #b91c1c;
  color: #fff;
}
.action-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
  margin-top: 20rpx;
}
.action-button {
  min-height: 144rpx;
  border: none;
  border-radius: 28rpx;
  background: #e6f6f2;
  color: var(--ss-color-text);
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
  line-height: 1.35;
  padding: 12rpx 20rpx;
}
.action-button.action-primary {
  background: linear-gradient(135deg, #d8fbf2 0%, #bdeee1 100%);
}
.action-button.action-warm {
  background: #fff0d2;
}
.action-button.action-danger {
  background: #fee2e2;
  color: #991b1b;
}
.action-button.action-muted {
  background: #eef2f7;
}
.summary-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
  margin-top: 16rpx;
}
.summary-item {
  padding: 22rpx 10rpx;
  border-radius: 22rpx;
  background: #f6f7f1;
  text-align: center;
}
.summary-num {
  display: block;
  font-size: var(--ss-font-size-title);
  font-weight: 700;
  color: var(--ss-color-primary);
}
.summary-label {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-caption);
  line-height: 1.5;
  color: var(--ss-color-subtext);
}
</style>
