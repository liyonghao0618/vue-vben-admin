<template>
  <view class="page-shell">
    <ss-topbar :title="selectedElder?.name || '与老人聊天'" :subtitle="selectedElder?.relation || '回访老人，先确认是否仍在操作可疑内容'" show-back />

    <ss-card v-if="selectedElder">
      <view class="tips-box">
        <text class="tips-title">当前守护建议</text>
        <text class="tips-text">{{ selectedElder.statusSummary }}</text>
        <text v-if="selectedElder.medicationNote" class="tips-text">补充提醒：{{ selectedElder.medicationNote }}</text>
        <text v-if="store.aiServiceNotice" class="tips-warning">{{ store.aiServiceNotice }}</text>
      </view>
    </ss-card>

    <view class="quick-row">
      <button class="quick-btn" @click="quickSend('先别转账，也不要告诉对方验证码。')">发送防骗提醒</button>
      <button class="quick-btn secondary" @click="quickSend('我现在正在看这条消息，你先别点任何链接。')">发送安抚消息</button>
    </view>
    <view class="quick-row">
      <button class="quick-btn warm" @click="sendOcrSample">同步截图 OCR 结果</button>
      <button class="quick-btn secondary" @click="sendCommunityNotice">通知社区协助</button>
    </view>

    <ss-feedback-state
      v-if="!selectedElder"
      empty
      empty-title="当前还没有选择老人"
      empty-description="请先从老人列表、风险通知或求助详情进入聊天回访。"
    />
    <ss-feedback-state
      v-else-if="!messages.length"
      empty
      empty-title="当前还没有回访消息"
      empty-description="可以先发送一条安抚消息或防骗提醒，后续这里会同步会话内容。"
    />

    <view class="message-list">
      <view
        v-for="message in messages"
        :key="message.id"
        class="message-item"
        :class="[`sender-${message.sender}`, `status-${message.status}`, { suspicious: message.suspicious }]"
      >
        <template v-if="message.type === 'image'">
          <view class="media-card">
            <text class="media-tag">图片消息预留</text>
            <text class="message-content">{{ message.content }}</text>
          </view>
        </template>
        <template v-else-if="message.type === 'link'">
          <view class="link-card">
            <text class="media-tag">链接消息预留</text>
            <text class="link-title">{{ message.linkTitle || '待校验链接' }}</text>
            <text class="link-url">{{ message.linkUrl }}</text>
            <text class="message-content">{{ message.content }}</text>
          </view>
        </template>
        <template v-else>
          <text class="message-content">{{ message.content }}</text>
        </template>

        <text v-if="message.riskReason" class="message-risk">{{ message.riskReason }}</text>
        <text class="message-meta">{{ message.time }} · {{ statusLabel(message.status) }}</text>
      </view>
    </view>

    <view class="composer">
      <input v-model="draft" class="composer-input" placeholder="输入回访消息或远程提醒内容" />
      <button class="send-button" @click="submitMessage">发送</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import { useAppStore } from '@/store/app'
import type { MessageStatus } from '@/types/app'

const store = useAppStore()
const draft = ref('')

const selectedElder = computed(() => store.selectedElder)
const messages = computed(() => store.selectedMessages)

function submitMessage() {
  store.sendMessage(draft.value)
  draft.value = ''
}

function quickSend(content: string) {
  store.sendMessage(content)
}

function sendOcrSample() {
  void store.sendImageMessage({
    title: '聊天截图复核',
    ocrText: '我是客服，请把验证码和银行卡拍给我处理补贴。',
  })
}

function sendCommunityNotice() {
  if (!selectedElder.value) {
    return
  }

  store.notifyCommunitySupport(selectedElder.value.id)
  uni.showToast({
    title: '已通知社区',
    icon: 'success',
  })
}

function statusLabel(status: MessageStatus) {
  const map: Record<MessageStatus, string> = {
    sent: '已发送',
    received: '收到回复',
    risk: '风险同步',
  }

  return map[status]
}
</script>

<style scoped lang="scss">
.page-shell {
  min-height: 100vh;
  padding: 32rpx 24rpx 160rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  background: linear-gradient(180deg, #f4f8fb 0%, #eef3ef 100%);
}
.tips-box {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.tips-title {
  font-size: 28rpx;
  font-weight: 700;
  color: var(--ss-color-primary);
}
.tips-text {
  font-size: 25rpx;
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.tips-warning {
  font-size: 23rpx;
  line-height: 1.6;
  color: #b45309;
}
.quick-row {
  display: flex;
  gap: 14rpx;
}
.quick-btn {
  flex: 1;
  border: none;
  border-radius: 18rpx;
  background: #dff7f2;
  color: var(--ss-color-primary);
  font-size: 24rpx;
  font-weight: 700;
}
.quick-btn.secondary {
  background: #eef2f7;
  color: var(--ss-color-text);
}
.quick-btn.warm {
  background: #fff0d2;
  color: #8a5a00;
}
.message-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.message-item {
  max-width: 82%;
  padding: 20rpx 22rpx;
  border-radius: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.message-item.sender-self {
  margin-left: auto;
  background: #dff7f2;
}
.message-item.sender-other {
  margin-right: auto;
  background: #ffffff;
}
.message-item.sender-system,
.message-item.status-risk,
.message-item.suspicious {
  width: 100%;
  max-width: 100%;
  background: #fff1f0;
  border: 2rpx solid #fecaca;
}
.message-content,
.link-title,
.link-url {
  font-size: 29rpx;
  line-height: 1.7;
}
.link-title {
  font-weight: 700;
}
.link-url,
.message-meta,
.media-tag,
.message-risk {
  font-size: 22rpx;
  color: var(--ss-color-subtext);
}
.message-risk {
  color: #b91c1c;
}
.media-card,
.link-card {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.composer {
  position: fixed;
  left: 24rpx;
  right: 24rpx;
  bottom: 24rpx;
  display: flex;
  gap: 16rpx;
  padding: 18rpx;
  border-radius: 26rpx;
  background: rgba(255, 253, 248, 0.96);
  box-shadow: 0 18rpx 40rpx rgba(22, 48, 43, 0.1);
}
.composer-input {
  flex: 1;
  height: 88rpx;
  padding: 0 20rpx;
  border-radius: 18rpx;
  background: #f3f5ef;
  font-size: 28rpx;
}
.send-button {
  width: 160rpx;
  border: none;
  border-radius: 18rpx;
  background: var(--ss-color-primary);
  color: #fff;
  font-size: 28rpx;
  font-weight: 700;
}
</style>
