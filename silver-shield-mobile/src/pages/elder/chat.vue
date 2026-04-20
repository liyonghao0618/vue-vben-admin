<template>
  <view class="page-shell">
    <ss-topbar :title="selectedContact?.name || '聊天会话'" :subtitle="selectedContact?.relation || '与守护人保持联系'" show-back />

    <ss-card>
      <view class="tips-box">
        <text class="tips-title">防骗提醒</text>
        <text class="tips-text">凡是提到验证码、转账、银行卡、陌生链接，先不要操作，先联系家属。</text>
        <text v-if="store.aiServiceNotice" class="tips-warning">{{ store.aiServiceNotice }}</text>
        <text class="tips-warning">已预留图片消息 OCR 识别，可把截图先发给家人核验。</text>
      </view>
    </ss-card>

    <ss-voice-bar
      :enabled="store.elderSettings.voiceBroadcastReserved"
      :text="selectedContact ? `正在与${selectedContact.name}聊天。风险提示：不要转账，不要点陌生链接。` : '聊天页已预留语音播报能力。'"
    />

    <ss-feedback-state
      v-if="!selectedContact"
      empty
      empty-title="当前还没有选择联系人"
      empty-description="请先从联系人列表或会话列表进入聊天页。"
    />
    <ss-feedback-state
      v-else-if="!messages.length"
      empty
      empty-title="当前会话还没有消息"
      empty-description="可以先发一句“我先问下家里人”，后续这里会展示消息和风险提示。"
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
      <input v-model="draft" class="composer-input" placeholder="输入消息，含转账/链接等关键词会触发提醒" />
      <button class="image-button" @click="sendImageSample">发截图</button>
      <button class="send-button" @click="submitMessage">发送</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import SsCard from '@/components/ui/ss-card.vue'
import SsFeedbackState from '@/components/ui/ss-feedback-state.vue'
import SsTopbar from '@/components/ui/ss-topbar.vue'
import SsVoiceBar from '@/components/ui/ss-voice-bar.vue'
import { useAppStore } from '@/store/app'
import type { MessageStatus } from '@/types/app'

const store = useAppStore()
const draft = ref('')

const selectedContact = computed(() => store.selectedContact)
const messages = computed(() => store.selectedMessages)

function submitMessage() {
  store.sendMessage(draft.value)
  draft.value = ''
}

function sendImageSample() {
  void store.sendImageMessage({
    title: '陌生短信截图',
    ocrText: '系统通知您补缴养老金，请点击链接并输入验证码。',
  })
}

function statusLabel(status: MessageStatus) {
  const map: Record<MessageStatus, string> = {
    sent: '已发送',
    received: '收到回复',
    risk: '风险提醒',
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
  background: linear-gradient(180deg, #f9f7f1 0%, #f0f4ef 100%);
}
.tips-box {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.tips-title {
  font-size: var(--ss-font-size-subtitle);
  font-weight: 700;
  color: #8a5a00;
}
.tips-text {
  font-size: var(--ss-font-size-body);
  line-height: 1.6;
  color: var(--ss-color-subtext);
}
.tips-warning {
  font-size: var(--ss-font-size-caption);
  line-height: 1.6;
  color: #b45309;
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
  font-size: var(--ss-font-size-body);
  line-height: 1.7;
}
.link-title {
  font-weight: 700;
}
.link-url,
.message-meta,
.media-tag,
.message-risk {
  font-size: var(--ss-font-size-caption);
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
  font-size: var(--ss-font-size-body);
}
.send-button {
  width: 160rpx;
  border: none;
  border-radius: 18rpx;
  background: var(--ss-color-primary);
  color: #fff;
  font-size: var(--ss-font-size-body);
  font-weight: 700;
}
.image-button {
  width: 140rpx;
  border: none;
  border-radius: 18rpx;
  background: #fff0d2;
  color: #8a5a00;
  font-size: var(--ss-font-size-caption);
  font-weight: 700;
}
</style>
