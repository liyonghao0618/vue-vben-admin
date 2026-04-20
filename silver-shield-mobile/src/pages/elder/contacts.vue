<template>
  <view class="page-shell">
    <ss-topbar title="联系人" subtitle="先联系最熟悉的人，陌生号码先核验。" show-back />
    <ss-voice-bar :enabled="store.elderSettings.voiceBroadcastReserved" text="联系人页已预留语音播报，可朗读联系人姓名、关系和联系建议。" />
    <ss-feedback-state
      v-if="!contacts.length"
      empty
      empty-title="联系人列表暂时为空"
      empty-description="完成绑定关系联调后，这里会展示家属、社区和熟人联系人。"
    />

    <ss-card v-for="contact in contacts" :key="contact.id">
      <view class="contact-row">
        <view class="avatar">{{ contact.avatarText }}</view>
        <view class="contact-main">
          <view class="name-row">
            <text class="name">{{ contact.name }}</text>
            <text v-if="contact.tag" class="tag">{{ contact.tag }}</text>
            <text v-if="contact.isPriority" class="tag priority">重点</text>
            <text v-if="contact.isBlacklisted" class="tag danger">黑名单</text>
            <text v-if="contact.suspiciousLevel && contact.suspiciousLevel !== 'none'" class="tag warm">可疑</text>
          </view>
          <text class="relation">{{ contact.relation }}</text>
          <text class="note">{{ contact.note }}</text>
          <text v-if="contact.supportsCommunityAssist" class="note">支持社区协同核验，可在高风险场景下请求协助。</text>
        </view>
      </view>
      <view class="action-row">
        <button class="mini-btn" @click="chatWith(contact.id)">发消息</button>
        <button class="mini-btn secondary" @click="startCall(contact.id)">语音通话</button>
      </view>
    </ss-card>

    <button class="record-button" @click="openPage('/pages/elder/call-records')">查看通话记录</button>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import SsVoiceBar from '@/components/ui/ss-voice-bar.vue'
import { useAppStore } from '@/store/app'
import { openPage } from '@/utils/navigation'

const store = useAppStore()
const contacts = computed(() => store.contacts)

function chatWith(contactId: string) {
  store.selectContact(contactId)
  openPage('/pages/elder/chat')
}

function startCall(contactId: string) {
  store.selectContact(contactId)
  store.startCall(contactId, 'elder', 'outgoing')
  openPage('/pages/elder/call')
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  background: #f7f3e9;
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
.name-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}
.name {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
}
.tag {
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  background: #fff0d2;
  color: #8a5a00;
  font-size: var(--ss-font-size-caption);
}
.tag.priority {
  background: #dff7f2;
  color: var(--ss-color-primary);
}
.tag.warm {
  background: #fff0d2;
  color: #8a5a00;
}
.tag.danger {
  background: #fee2e2;
  color: #991b1b;
}
.relation,
.note {
  display: block;
  margin-top: 8rpx;
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-subtext);
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
.record-button {
  border: none;
  border-radius: 20rpx;
  background: #eef2f7;
  color: var(--ss-color-text);
  font-size: var(--ss-font-size-body);
}
</style>
