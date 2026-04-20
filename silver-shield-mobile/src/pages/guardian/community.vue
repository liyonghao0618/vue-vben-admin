<template>
  <view class="page-shell">
    <ss-topbar title="社区协同" subtitle="高风险、求助未接通或需要上门核验时，可同步社区跟进。" show-back />

    <ss-card>
      <ss-section-title title="当前可协同资源" subtitle="先保留入口和协同文案，后续可接真实工单系统。" />
      <view class="summary-box">
        <text class="summary-text">可用社区联系人 {{ contacts.length }} 位</text>
        <text class="summary-text">待跟进风险 {{ store.guardianRiskRecords.filter((item) => item.followUpStatus !== 'resolved').length }} 条</text>
      </view>
    </ss-card>

    <ss-feedback-state
      v-if="!contacts.length"
      empty
      empty-title="当前没有社区协同联系人"
      empty-description="完成社区协同接口联调后，这里会展示网格员、社工或志愿者联系人。"
    />

    <ss-card v-for="contact in contacts" :key="contact.id">
      <view class="contact-row">
        <view class="avatar">{{ contact.avatarText }}</view>
        <view class="contact-main">
          <text class="name">{{ contact.name }}</text>
          <text class="meta">{{ contact.relation }}</text>
          <text class="meta">{{ contact.note }}</text>
        </view>
      </view>
      <view class="action-row">
        <button class="mini-btn" @click="notifyCommunity(contact.id)">发起协同</button>
        <button class="mini-btn secondary" @click="callCommunity(contact.id)">语音联系</button>
      </view>
    </ss-card>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsSectionTitle from '@/components/ui/ss-section-title.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
const contacts = computed(() => store.communityContacts)

function notifyCommunity(contactId: string) {
  store.notifyCommunitySupport(store.selectedElderId)
  store.selectContact(contactId)
  uni.showToast({
    title: '已发起协同',
    icon: 'success',
  })
}

function callCommunity(contactId: string) {
  store.selectContact(contactId)
  store.startCall(contactId, 'guardian', 'outgoing')
  openPage('/pages/guardian/call')
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  background: #eef7f1;
}
.summary-box {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  margin-top: 16rpx;
}
.summary-text,
.meta {
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.contact-row {
  display: flex;
  gap: 18rpx;
}
.avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  background: #dff7f2;
  color: var(--ss-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 700;
}
.contact-main {
  flex: 1;
}
.name {
  display: block;
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
.action-row {
  display: flex;
  gap: 14rpx;
  margin-top: 20rpx;
}
.mini-btn {
  flex: 1;
  border: none;
  border-radius: 18rpx;
  background: var(--ss-color-primary);
  color: #fff;
  font-size: var(--ss-font-size-body);
}
.mini-btn.secondary {
  background: #eef2f7;
  color: var(--ss-color-text);
}
</style>
